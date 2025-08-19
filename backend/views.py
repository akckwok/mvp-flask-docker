import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from .models import Job, User, db
from . import pipeline_manager
from .config import UPLOADS_DIR
from flask_login import login_user, current_user, logout_user, login_required
from .forms import RegistrationForm, LoginForm
from .extensions import bcrypt

api = Blueprint('api', __name__)

@api.route('/register', methods=['POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return jsonify({'message': 'Registration successful'}), 201
    return jsonify({'errors': form.errors}), 400

@api.route('/login', methods=['POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            return jsonify({'message': 'Login successful'})
        else:
            return jsonify({'error': 'Login Unsuccessful. Please check username and password'}), 401
    return jsonify({'errors': form.errors}), 400

@api.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logout successful'})

@api.route('/user')
@login_required
def get_user():
    return jsonify({'username': current_user.username})

@api.route('/pipelines')
@login_required
def get_pipelines():
    return jsonify(current_app.config['AVAILABLE_PIPELINES'])

@api.route('/upload', methods=['POST'])
@login_required
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
            filename = f"{job_id}_{file.filename}"
            filepath = os.path.join(UPLOADS_DIR, filename)
            file.save(filepath)
            job_files.append({
                'original_filename': file.filename,
                'filepath': filepath
            })

    new_job = Job(id=job_id, files=job_files, user_id=current_user.id)
    db.session.add(new_job)
    db.session.commit()

    return jsonify({
        'jobId': new_job.id,
        'filenames': [f['original_filename'] for f in new_job.files]
    })

@api.route('/run-job', methods=['POST'])
@login_required
def run_job():
    data = request.get_json()
    job_id = data.get('jobId')
    pipeline_id = data.get('pipelineId')

    if not job_id or not pipeline_id:
        return jsonify({'error': 'Missing jobId or pipelineId'}), 400

    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first()
    if not job:
        return jsonify({'error': 'Job not found'}), 404

    available_pipelines = current_app.config['AVAILABLE_PIPELINES']
    pipeline = next((p for p in available_pipelines if p['id'] == pipeline_id), None)
    if not pipeline:
        return jsonify({'error': 'Pipeline not found'}), 404

    filenames = [os.path.basename(f['filepath']) for f in job.files]
    process = pipeline_manager.run_pipeline(pipeline, job.id, filenames)

    if process is None:
        return jsonify({'error': 'Failed to start pipeline process'}), 500

    job.status = 'running'
    job.pipeline = pipeline_id
    job.container_id = process.id
    db.session.commit()

    return jsonify({
        'message': f"Job '{job.id}' started with pipeline '{pipeline_id}'.",
    })

@api.route('/jobs')
@login_required
def get_jobs():
    jobs = Job.query.filter_by(user_id=current_user.id).all()
    return jsonify([job.to_dict() for job in jobs])
