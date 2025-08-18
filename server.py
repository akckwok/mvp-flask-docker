import os
import subprocess
import uuid
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# In-memory store for job information
# In a real app, you would use a database (e.g., Redis, PostgreSQL)
jobs_db = {}
UPLOADS_DIR = 'uploads'

# Serve the main HTML file from the public directory
@app.route('/')
def serve_index():
    return send_from_directory('dashboard-ui/public', 'index.html')

# Serve other static files from the public directory (e.g., CSS)
@app.route('/<path:filename>')
def serve_public(filename):
    return send_from_directory('dashboard-ui/public', filename)

# Serve JavaScript module files from the src directory
@app.route('/src/<path:filename>')
def serve_src(filename):
    return send_from_directory('dashboard-ui/src', filename)

# API endpoint to get the list of available pipelines
@app.route('/api/pipelines')
def get_pipelines():
    pipeline_dir = './pipelines'
    try:
        pipelines = [d for d in os.listdir(pipeline_dir) if os.path.isdir(os.path.join(pipeline_dir, d))]
        return jsonify(pipelines)
    except FileNotFoundError:
        return jsonify({'error': 'Pipelines directory not found'}), 404

# API endpoint to handle file uploads
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file:
        job_id = str(uuid.uuid4())
        # Sanitize filename for security in a real app
        filename = f"{job_id}_{file.filename}"
        filepath = os.path.join(UPLOADS_DIR, filename)

        file.save(filepath)

        jobs_db[job_id] = {
            'original_filename': file.filename,
            'filepath': filepath,
            'status': 'uploaded'
        }

        return jsonify({'jobId': job_id, 'filename': file.filename})

# API endpoint to run a job
@app.route('/api/run-job', methods=['POST'])
def run_job():
    data = request.get_json()
    job_id = data.get('jobId')
    pipeline_name = data.get('pipelineName')

    if not job_id or not pipeline_name:
        return jsonify({'error': 'Missing jobId or pipelineName'}), 400

    job_info = jobs_db.get(job_id)
    if not job_info:
        return jsonify({'error': 'Job not found'}), 404

    # This is where you would trigger the actual Docker process
    # For now, we just simulate the command
    docker_image_name = f"{pipeline_name}-image"
    # Note: In a real-world scenario, mounting volumes like this requires careful
    # security considerations to prevent directory traversal attacks.
    docker_command = f"docker run --rm -v {os.path.abspath(UPLOADS_DIR)}:/data {docker_image_name}"

    jobs_db[job_id]['status'] = 'running'
    jobs_db[job_id]['pipeline'] = pipeline_name

    print(f"Executing job {job_id} with pipeline {pipeline_name}.")
    print(f"Simulated command: {docker_command}")

    return jsonify({
        'message': f"Job '{job_id}' started with pipeline '{pipeline_name}'.",
        'docker_command_simulation': docker_command
    })


if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    if not os.path.exists(UPLOADS_DIR):
        os.makedirs(UPLOADS_DIR)

    # Build Docker images for all pipelines on startup.
    print("Attempting to build Docker images for all pipelines...")
    try:
        pipeline_dir = './pipelines'
        pipelines = [d for d in os.listdir(pipeline_dir) if os.path.isdir(os.path.join(pipeline_dir, d))]
        for pipeline in pipelines:
            image_name = f"{pipeline}-image"
            pipeline_path = os.path.join(pipeline_dir, pipeline)
            print(f"Building image '{image_name}' from '{pipeline_path}'...")
            # Using capture_output=True to hide verbose build logs unless there's an error
            result = subprocess.run(
                ['docker', 'build', '-t', image_name, pipeline_path],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"Image '{image_name}' built successfully.")

    except FileNotFoundError:
        print("Could not build Docker images: 'docker' command not found. Please ensure Docker is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error building Docker image for '{pipeline}'. Please ensure Docker is running.")
        print(f"Stderr:\n{e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred during Docker image build: {e}")

    app.run(host='0.0.0.0', debug=True, port=5000)
