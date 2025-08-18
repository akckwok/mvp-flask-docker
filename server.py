import os
import subprocess
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

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

# API endpoint to handle file uploads
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file:
        # In a real app, you'd save the file and process it.
        # Here, we just acknowledge receipt and return a simulated command.
        print(f"File '{file.filename}' received. Simulating Docker process.")

        return jsonify({
            'message': f"File '{file.filename}' received. Processing started.",
            'docker_command_simulation': 'docker run --rm -v /uploads:/data word-counter-image'
        })

if __name__ == '__main__':
    # Build the Docker image on startup if it doesn't exist.
    print("Attempting to build word-counter Docker image...")
    try:
        subprocess.run(
            ['docker', 'build', '-t', 'word-counter-image', './pipelines/word-counter'],
            check=True,
            capture_output=True,
            text=True
        )
        print("Docker image 'word-counter-image' built successfully.")
    except FileNotFoundError:
        print("Could not build Docker image: 'docker' command not found. Please ensure Docker is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        print(f"Error building Docker image. Please ensure Docker is running.")
        print(f"Stderr: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred during Docker image build: {e}")

    app.run(host='0.0.0.0', debug=True, port=5000)
