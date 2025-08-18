import os
import subprocess
import uuid
import threading
import re
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# In-memory store for job information.
# A lock is needed for thread-safe access to the shared jobs_db dictionary.
jobs_db = {}
db_lock = threading.Lock()
UPLOADS_DIR = 'uploads'

def monitor_pipeline(job_id):
    """
    This function runs in a background thread to monitor the output of a
    running Docker container and parse its progress.
    """
    print(f"[{job_id}] Starting monitoring thread.", flush=True)

    with db_lock:
        process = jobs_db[job_id]['process']

    # Regex to parse "Steps: X/Y [Process Title]"
    progress_regex = re.compile(r"Steps: (\d+)/(\d+) \[(.*?)\]")

    # Read stdout line by line in a non-blocking way
    for line in iter(process.stdout.readline, ''):
        line = line.strip()
        if not line:
            continue

        print(f"[{job_id}] RAW_LOG: {line}", flush=True)

        match = progress_regex.match(line)
        if match:
            current_step = int(match.group(1))
            total_steps = int(match.group(2))
            process_title = match.group(3)
            # Ensure total_steps is not zero to avoid division errors
            progress = int((current_step / total_steps) * 100) if total_steps > 0 else 0

            with db_lock:
                jobs_db[job_id].update({
                    'current_step': current_step,
                    'total_steps': total_steps,
                    'process_title': process_title,
                    'progress': progress,
                })
            print(f"[{job_id}] Parsed progress: {progress}% - {process_title}", flush=True)

    # After the stdout stream is closed, wait for the process to terminate
    process.wait()
    # Read any remaining error output
    error_output = process.stderr.read().strip()

    with db_lock:
        print(f"[{job_id}] Process finished with exit code: {process.returncode}", flush=True)
        if process.returncode == 0:
            jobs_db[job_id]['status'] = 'completed'
            jobs_db[job_id]['progress'] = 100
            jobs_db[job_id]['process_title'] = 'Completed'
        else:
            jobs_db[job_id]['status'] = 'error'
            # Be verbose with the error message
            error_summary = error_output or "Pipeline failed with no error message."
            jobs_db[job_id]['process_title'] = f"Error: {error_summary[:250]}" # Truncate for UI
            print(f"[{job_id}] Stored error: {error_summary}", flush=True)
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
    pipeline_dir = './pipelines'
    try:
        pipelines = [d for d in os.listdir(pipeline_dir) if os.path.isdir(os.path.join(pipeline_dir, d))]
        return jsonify(pipelines)
    except FileNotFoundError:
        return jsonify({'error': 'Pipelines directory not found'}), 404

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    job_id = str(uuid.uuid4())
    filename = f"{job_id}_{file.filename}"
    filepath = os.path.join(UPLOADS_DIR, filename)
    file.save(filepath)

    with db_lock:
        jobs_db[job_id] = {
            'original_filename': file.filename,
            'filepath': filepath,
            'status': 'preparing',
            'pipeline': None,
            'process': None,
            'progress': 0,
            'current_step': 0,
            'total_steps': 0,
            'process_title': 'Awaiting Selection'
        }

    return jsonify({'jobId': job_id, 'filename': file.filename})

@app.route('/api/run-job', methods=['POST'])
def run_job():
    data = request.get_json()
    job_id = data.get('jobId')
    pipeline_name = data.get('pipelineName')

    if not job_id or not pipeline_name:
        return jsonify({'error': 'Missing jobId or pipelineName'}), 400

    with db_lock:
        if job_id not in jobs_db:
            return jsonify({'error': 'Job not found'}), 404
        job_info = jobs_db[job_id]

    docker_image_name = f"{pipeline_name}-image"
    file_to_process = os.path.basename(job_info['filepath'])

    docker_command = [
        'sudo', 'docker', 'run', '--rm',
        '-v', f"{os.path.abspath(UPLOADS_DIR)}:/data",
        docker_image_name, file_to_process
    ]

    try:
        process = subprocess.Popen(
            docker_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, # Keep stderr separate to capture errors
            text=True,
            bufsize=1,
            universal_newlines=True
        )
    except Exception as e:
        return jsonify({'error': f'Failed to start Docker container: {e}'}), 500

    with db_lock:
        job_info.update({
            'status': 'running',
            'pipeline': pipeline_name,
            'process': process,
            'process_title': 'Initializing pipeline...'
        })

    monitor_thread = threading.Thread(target=monitor_pipeline, args=(job_id,))
    monitor_thread.start()

    print(f"[{job_id}] Job started with pipeline '{pipeline_name}'.", flush=True)
    return jsonify({'message': f"Job '{job_id}' started successfully."})

@app.route('/api/job-status/<job_id>')
def get_job_status(job_id):
    with db_lock:
        job_info = jobs_db.get(job_id)

    if not job_info:
        return jsonify({'error': 'Job not found'}), 404

    return jsonify({
        'jobId': job_id,
        'status': job_info.get('status'),
        'progress': job_info.get('progress'),
        'current_step': job_info.get('current_step'),
        'total_steps': job_info.get('total_steps'),
        'process_title': job_info.get('process_title'),
    })

if __name__ == '__main__':
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)

    print("Attempting to build Docker images for all pipelines...", flush=True)
    try:
        pipeline_dir = './pipelines'
        pipelines = [d for d in os.listdir(pipeline_dir) if os.path.isdir(os.path.join(pipeline_dir, d))]
        for pipeline in pipelines:
            image_name = f"{pipeline}-image"
            pipeline_path = os.path.join(pipeline_dir, pipeline)
            print(f"Building image '{image_name}' from '{pipeline_path}'...", flush=True)
            result = subprocess.run(
                ['sudo', 'docker', 'build', '-t', image_name, pipeline_path],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"Image '{image_name}' built successfully.", flush=True)
    except FileNotFoundError:
        print("Could not build Docker images: 'docker' command not found. Please add user to the 'docker' group or install Docker.", flush=True)
    except subprocess.CalledProcessError as e:
        print(f"Error building Docker image for '{pipeline}'. Stderr:\n{e.stderr}", flush=True)
    except Exception as e:
        print(f"An unexpected error occurred during Docker image build: {e}", flush=True)

    app.run(host='0.0.0.0', debug=True, port=5000, use_reloader=False)
