import os
import subprocess
import uuid
from flask import Flask, request, jsonify, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from database import db
from user import User

def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./instance/project.db'

    if config_overrides:
        app.config.update(config_overrides)

    if not os.path.exists('instance'):
        os.makedirs('instance')

    db.init_app(app)
    bcrypt = Bcrypt(app)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)

    # In-memory store for job information
    jobs_db = {}
    UPLOADS_DIR = 'uploads'

    # Serve the login page
    @app.route('/')
    def login():
        return send_from_directory('dashboard-ui/public', 'login.html')

    @app.route('/register.html')
    def register():
        return send_from_directory('dashboard-ui/public', 'register.html')

    # Serve the main HTML file from the public directory
    @app.route('/dashboard')
    @login_required
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

    # API endpoint for user login
    @app.route('/api/login', methods=['POST'])
    def api_login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

    @app.route('/api/register', methods=['POST'])
    def api_register():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Username already exists'}), 400

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'success': True, 'message': 'User created successfully'})

    # API endpoint for user logout
    @app.route('/api/logout', methods=['POST'])
    @login_required
    def logout():
        logout_user()
        return jsonify({'success': True})

    # API endpoint to check auth status
    @app.route('/api/check-auth')
    def check_auth():
        return jsonify({'is_authenticated': current_user.is_authenticated})

    # API endpoint to get the list of available pipelines
    @app.route('/api/pipelines')
    @login_required
    def get_pipelines():
        pipeline_dir = './pipelines'
        try:
            pipelines = [d for d in os.listdir(pipeline_dir) if os.path.isdir(os.path.join(pipeline_dir, d))]
            return jsonify(pipelines)
        except FileNotFoundError:
            return jsonify({'error': 'Pipelines directory not found'}), 404

    # API endpoint to handle file uploads
    @app.route('/api/upload', methods=['POST'])
    @login_required
    def upload_file():
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in the request'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if file:
            job_id = str(uuid.uuid4())
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
    @login_required
    def run_job():
        data = request.get_json()
        job_id = data.get('jobId')
        pipeline_name = data.get('pipelineName')

        if not job_id or not pipeline_name:
            return jsonify({'error': 'Missing jobId or pipelineName'}), 400

        job_info = jobs_db.get(job_id)
        if not job_info:
            return jsonify({'error': 'Job not found'}), 404

        docker_image_name = f"{pipeline_name}-image"
        docker_command = f"docker run --rm -v {os.path.abspath(UPLOADS_DIR)}:/data {docker_image_name}"

        jobs_db[job_id]['status'] = 'running'
        jobs_db[job_id]['pipeline'] = pipeline_name

        print(f"Executing job {job_id} with pipeline {pipeline_name}.")
        print(f"Simulated command: {docker_command}")

        return jsonify({
            'message': f"Job '{job_id}' started with pipeline '{pipeline_name}'.",
            'docker_command_simulation': docker_command
        })

    return app
