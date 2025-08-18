import os
import subprocess
from flask import Flask, request, jsonify, send_from_directory

# The 'static_folder' points to the directory where your front-end is.
app = Flask(__name__, static_folder='static', static_url_path='')

# Route to serve the main index.html file
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# API endpoint to handle file uploads
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file:
        # In a real app, you would save the file securely and pass its path
        # to the Docker container.
        # For this MVP, we just simulate the Docker command.
        print(f"File '{file.filename}' received. Simulating Docker process.")

        # --- This is where you would run the Docker command ---
        # Example:
        # try:
        #     subprocess.run(['docker', 'run', '--rm', 'word-counter-image'], check=True)
        #     print("Docker container ran successfully.")
        # except Exception as e:
        #     print(f"Error running Docker: {e}")
        # ---------------------------------------------------------

        return jsonify({
            'message': f"File '{file.filename}' received. Processing started.",
            'docker_command_simulation': 'docker run --rm word-counter-image'
        })

if __name__ == '__main__':
    # It's a good practice to build the Docker image once on startup if it doesn't exist
    print("Building word-counter Docker image...")
    try:
        subprocess.run(
            ['docker', 'build', '-t', 'word-counter-image', './pipelines/word-counter'],
            check=True
        )
        print("Docker image built successfully.")
    except Exception as e:
        print(f"Could not build Docker image. Please ensure Docker is running. Error: {e}")

    app.run(host='0.0.0.0', debug=True, port=5000)
