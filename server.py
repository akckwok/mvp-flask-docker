import os
import uuid
from flask import Flask, request, jsonify, send_from_directory
import pipeline_manager

app = Flask(__name__)

# In-memory stores for job and pipeline information
jobs_db = {}
available_pipelines = []
UPLOADS_DIR = 'uploads'

# --- HTML Serving ---

@app.route('/')
def serve_index():
    return send_from_directory('dashboard-ui/public', 'index.html')

@app.route('/<path:filename>')
def serve_public(filename):
    return send_from_directory('dashboard-ui/public', filename)

@app.route('/src/<path:filename>')
def serve_src(filename):
    return send_from_directory('dashboard-ui/src', filename)

# --- API Endpoints ---

@app.route('/api/pipelines')
def get_pipelines():
    return jsonify(available_pipelines)

@app.route('/api/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files part in the request'}), 400

    files = request.files.getlist('files')

    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No files selected'}), 400

    job_id = str(uuid.uuid4())
    job_files = []

    for file in files:
        if file:
            # In a real app, you'd want to sanitize filenames properly
            filename = f"{job_id}_{file.filename}"
            filepath = os.path.join(UPLOADS_DIR, filename)
            file.save(filepath)
            job_files.append({
                'original_filename': file.filename,
                'filepath': filepath
            })

    jobs_db[job_id] = {
        'files': job_files,
        'status': 'uploaded'
    }

    return jsonify({
        'jobId': job_id,
        'filenames': [f['original_filename'] for f in job_files]
    })

@app.route('/api/run-job', methods=['POST'])
def run_job():
    data = request.get_json()
    job_id = data.get('jobId')
    pipeline_id = data.get('pipelineId')

    if not job_id or not pipeline_id:
        return jsonify({'error': 'Missing jobId or pipelineId'}), 400

    job_info = jobs_db.get(job_id)
    if not job_info:
        return jsonify({'error': 'Job not found'}), 404

    pipeline = next((p for p in available_pipelines if p['id'] == pipeline_id), None)
    if not pipeline:
        return jsonify({'error': 'Pipeline not found'}), 404

    # Get the relative path for the files for the container
    filenames = [os.path.basename(f['filepath']) for f in job_info['files']]

    # This now calls the actual execution function
    process = pipeline_manager.run_pipeline(pipeline, job_id, filenames)

    if process is None:
        return jsonify({'error': 'Failed to start pipeline process'}), 500

    jobs_db[job_id]['status'] = 'running'
    jobs_db[job_id]['pipeline'] = pipeline_id
    jobs_db[job_id]['process_pid'] = process.pid

    return jsonify({
        'message': f"Job '{job_id}' started with pipeline '{pipeline_id}'.",
    })

@app.route('/api/jobs')
def get_jobs():
    # Return a list of jobs, sorted by a 'created_at' timestamp if available
    # For now, we'll just return the dictionary as a list of its values
    return jsonify(list(jobs_db.values()))

# --- Main Application Setup ---

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)

    # Discover and build pipelines on startup
    print("--- Initializing Pipelines ---")
    available_pipelines = pipeline_manager.discover_pipelines()
    if not available_pipelines:
        print("Warning: No pipelines found. Please check the 'pipelines' directory.")
    else:
        print(f"Found {len(available_pipelines)} pipelines: {[p['name'] for p in available_pipelines]}")
        # In a real CI/CD environment, pipelines would be pre-built.
        # To avoid issues with Docker Hub rate limits in this environment,
        # we are skipping the build step.
        # try:
        #     pipeline_manager.build_pipelines(available_pipelines)
        #     print("--- Pipeline initialization complete ---")
        # except Exception as e:
        #     print(f"Fatal error during pipeline initialization: {e}")
        #     exit(1)
        print("--- Pipeline building on startup is disabled ---")

    app.run(host='0.0.0.0', debug=True, port=5000)
