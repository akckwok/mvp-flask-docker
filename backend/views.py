import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from .models import Job, User, db, Project, Skill, LabMember, DataSubmission
from . import pipeline_manager
from .config import UPLOADS_DIR
from flask_login import login_user, current_user, logout_user, login_required
from .forms import RegistrationForm, LoginForm
from .extensions import bcrypt
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/register', methods=['POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(
            username=form.username.data,
            full_name=form.full_name.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            password_hash=hashed_password
        )
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

@api.route('/profile')
@login_required
def get_profile():
    return jsonify({
        'username': current_user.username,
        'full_name': current_user.full_name,
        'email': current_user.email,
        'phone_number': current_user.phone_number
    })

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


@api.route('/projects', methods=['GET'])
def get_projects():
    projects = Project.query.all()
    return jsonify([project.to_dict() for project in projects])


@api.route('/submit_project', methods=['POST'])
@login_required
def submit_project():
    data = request.get_json()
    start_date = datetime.strptime(data['start-date'], '%Y-%m-%d').date()
    new_project = Project(
        id=data['project-name'],  # Using project name as ID
        project_name=data['project-name'],
        project_lead=data['project-lead'],
        start_date=start_date,
        status=data['status'],
        description=data.get('description'),
        sample_type=data.get('sample-type'),
        sequencing_method=data.get('sequencing-method'),
        year=start_date.year
    )
    db.session.add(new_project)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Project submitted successfully!'})


@api.route('/skills', methods=['GET'])
def get_skills():
    skills = Skill.query.all()
    return jsonify([skill.name for skill in skills])


@api.route('/skills', methods=['POST'])
@login_required
def add_skill():
    data = request.get_json()
    new_skill_name = data.get('skill')
    if new_skill_name:
        existing_skill = Skill.query.filter_by(name=new_skill_name).first()
        if not existing_skill:
            new_skill = Skill(name=new_skill_name)
            db.session.add(new_skill)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Skill added successfully!'})
    return jsonify({'success': False, 'message': 'Skill already exists or is invalid.'})


@api.route('/submit', methods=['POST'])
@login_required
def submit_lab_member():
    data = request.get_json()
    start_date = datetime.strptime(data['start-date'], '%Y-%m-%d').date() if data.get('start-date') else None
    end_date = datetime.strptime(data['end-date'], '%Y-%m-%d').date() if data.get('end-date') else None

    new_member = LabMember(
        name=data['name'],
        email=data['email'],
        phone=data.get('phone'),
        role=data['role'],
        status=data['status'],
        start_date=start_date,
        end_date=end_date,
        projects=data.get('projects'),
        responsibilities=data.get('responsibilities')
    )

    if 'skills' in data:
        for skill_name in data['skills']:
            skill = Skill.query.filter_by(name=skill_name).first()
            if skill:
                new_member.skills.append(skill)

    db.session.add(new_member)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Lab member profile created successfully!'})


@api.route('/members', methods=['GET'])
def get_members():
    members = LabMember.query.all()
    return jsonify([member.to_dict() for member in members])


@api.route('/submit_data', methods=['POST'])
@login_required
def submit_data():
    # This endpoint needs to handle file uploads as well as form data.
    # The provided HTML uses FormData, so we need to access fields from `request.form`
    # and files from `request.files`.

    # For simplicity in this step, we'll assume the file paths are just stored as strings.
    # A full implementation would save the files and store the paths.

    extraction_date = datetime.strptime(request.form['extraction-date'], '%Y-%m-%d').date()
    submission_date = datetime.strptime(request.form['submission-date'], '%Y-%m-%d').date()

    new_submission = DataSubmission(
        project_id=request.form['project-id'],
        sample_ids=request.form['sample-ids'],
        extraction_date=extraction_date,
        extracted_by=request.form['extracted-by'],
        extraction_method=request.form['extraction-method'],
        method_modifications=request.form.get('method-modifications'),
        sequencing_method=request.form['sequencing-method'],
        primers_used=request.form.get('primers-used'),
        submitted_to=request.form['submitted-to'],
        submission_date=submission_date,
        # Storing filenames for now. In a real app, you'd handle the file upload here.
        raw_data_file=request.files.get('raw-data-file').filename if 'raw-data-file' in request.files else None,
        provenance_email=request.files.get('provenance-email').filename if 'provenance-email' in request.files else None
    )
    db.session.add(new_submission)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Data submission successful!'})
