import os
import subprocess
import uuid
import threading
import re
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# --- Globals ---
jobs_db = {}
db_lock = threading.Lock()
UPLOADS_DIR = 'uploads'
VALID_PIPELINES = [] # Populated at startup with compliant pipelines

# --- Business Logic & Helpers ---

def validate_pipeline(pipeline_name):
    """
    Checks if a given pipeline is compliant with project standards.
    A compliant pipeline must have a Dockerfile containing an ENTRYPOINT.
    Returns (True, None) if valid, (False, error_message) if invalid.
    """
    pipeline_path = os.path.join('./pipelines', pipeline_name)
    dockerfile_path = os.path.join(pipeline_path, 'Dockerfile')

    # Check 1: Dockerfile must exist.
    if not os.path.exists(dockerfile_path):
        return False, f"Skipping pipeline '{pipeline_name}': 'Dockerfile' not found."

    # Check 2: Dockerfile must contain an ENTRYPOINT instruction.
    try:
        with open(dockerfile_path, 'r') as f:
            if 'ENTRYPOINT' not in f.read():
                return False, f"Skipping pipeline '{pipeline_name}': Dockerfile is missing the required 'ENTRYPOINT' instruction."
    except Exception as e:
        return False, f"Skipping pipeline '{pipeline_name}': Could not read Dockerfile. Error: {e}"

    return True, None

def monitor_pipeline(job_id):
    """
    Monitors a running Docker container in a background thread, parsing its
    output for progress and updating the job's status in the database.
    """
    print(f"[{job_id}] Starting monitoring thread.", flush=True)
    with db_lock:
        process = jobs_db[job_id]['process']

    progress_regex = re.compile(r"Steps: (\d+)/(\d+) \[(.*?)\]")
    for line in iter(process.stdout.readline, ''):
        line = line.strip()
        if not line: continue
        print(f"[{job_id}] RAW_LOG: {line}", flush=True)
        match = progress_regex.match(line)
        if match:
            with db_lock:
                jobs_db[job_id].update({
                    'current_step': int(match.group(1)),
                    'total_steps': int(match.group(2)),
                    'process_title': match.group(3),
                    'progress': int((int(match.group(1)) / int(match.group(2))) * 100) if int(match.group(2)) > 0 else 0,
                })

    process.wait()
    error_output = process.stderr.read().strip()
    with db_lock:
        print(f"[{job_id}] Process finished with exit code: {process.returncode}", flush=True)
        if process.returncode == 0:
            jobs_db[job_id].update({'status': 'completed', 'progress': 100, 'process_title': 'Completed'})
        else:
            error_summary = error_output or "Pipeline failed with no error message."
            jobs_db[job_id].update({'status': 'error', 'process_title': f"Error: {error_summary[:250]}"})
        print(f"[{job_id}] Monitoring finished. Status: {jobs_db[job_id]['status']}", flush=True)

# --- Flask Routes ---

@app.route('/')
def serve_index():
    return send_from_directory('dashboard-ui/public', 'index.html')

@app.route('/<path:filename>')
def serve_public(filename):
    return send_from_directory('dashboard-ui/public', filename)

@app.route('/src/<path:filename>')
def serve_src(filename):
    return send_from_directory('dashboard-ui/src', filename)

@app.route('/api/pipelines')
def get_pipelines():
    return jsonify(VALID_PIPELINES)

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No file selected'}), 400

    job_id = str(uuid.uuid4())
    filename = f"{job_id}_{file.filename}"
    filepath = os.path.join(UPLOADS_DIR, filename)
    file.save(filepath)

    with db_lock:
        jobs_db[job_id] = {
            'filepath': filepath, 'status': 'preparing', 'progress': 0,
            'process_title': 'Awaiting Selection'
        }
    return jsonify({'jobId': job_id, 'filename': file.filename})

@app.route('/api/run-job', methods=['POST'])
def run_job():
    data = request.get_json()
    job_id, pipeline_name = data.get('jobId'), data.get('pipelineName')
    if not all([job_id, pipeline_name]): return jsonify({'error': 'Missing jobId or pipelineName'}), 400
    if pipeline_name not in VALID_PIPELINES: return jsonify({'error': 'Invalid or unavailable pipeline'}), 400

    with db_lock:
        if job_id not in jobs_db: return jsonify({'error': 'Job not found'}), 404
        job_info = jobs_db[job_id]

    image_name = f"{pipeline_name}-image"
    file_to_process = os.path.basename(job_info['filepath'])
    docker_command = ['sudo', 'docker', 'run', '--rm', '-v', f"{os.path.abspath(UPLOADS_DIR)}:/data", image_name, file_to_process]

    try:
        process = subprocess.Popen(docker_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)
    except Exception as e:
        return jsonify({'error': f'Failed to start Docker container: {e}'}), 500

    with db_lock:
        job_info.update({'status': 'running', 'pipeline': pipeline_name, 'process': process, 'process_title': 'Initializing...'})

    threading.Thread(target=monitor_pipeline, args=(job_id,)).start()
    return jsonify({'message': f"Job '{job_id}' started."})

@app.route('/api/job-status/<job_id>')
def get_job_status(job_id):
    with db_lock:
        job_info = jobs_db.get(job_id)
    if not job_info: return jsonify({'error': 'Job not found'}), 404
    return jsonify({k: job_info.get(k) for k in ['status', 'progress', 'current_step', 'total_steps', 'process_title']})

# --- Main Execution ---

if __name__ == '__main__':
    if not os.path.exists(UPLOADS_DIR): os.makedirs(UPLOADS_DIR)

    print("--- Initializing & Validating Pipelines ---", flush=True)
    pipeline_dir = './pipelines'
    if os.path.isdir(pipeline_dir):
        for pipeline_name in os.listdir(pipeline_dir):
            if os.path.isdir(os.path.join(pipeline_dir, pipeline_name)):
                is_valid, error_msg = validate_pipeline(pipeline_name)
                if not is_valid:
                    print(f"Validation Error: {error_msg}", flush=True)
                    continue

                print(f"Pipeline '{pipeline_name}' passed validation. Building image...", flush=True)
                image_name = f"{pipeline_name}-image"
                try:
                    subprocess.run(['sudo', 'docker', 'build', '-t', image_name, os.path.join(pipeline_dir, pipeline_name)], check=True, capture_output=True, text=True)
                    VALID_PIPELINES.append(pipeline_name)
                    print(f"Image '{image_name}' built successfully.", flush=True)
                except Exception as e:
                    print(f"Error building Docker image for '{pipeline_name}': {e}", flush=True)

    print(f"--- Initialization Complete. Serving {len(VALID_PIPELINES)} pipeline(s): {VALID_PIPELINES} ---", flush=True)
    app.run(host='0.0.0.0', debug=True, port=5000, use_reloader=False)
