import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from .models import Job, db
from . import pipeline_manager
from .config import UPLOADS_DIR

api = Blueprint('api', __name__)

@api.route('/pipelines')
def get_pipelines():
    return jsonify(current_app.config['AVAILABLE_PIPELINES'])

@api.route('/upload', methods=['POST'])
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

    new_job = Job(id=job_id, files=job_files)
    db.session.add(new_job)
    db.session.commit()

    return jsonify({
        'jobId': new_job.id,
        'filenames': [f['original_filename'] for f in new_job.files]
    })

@api.route('/run-job', methods=['POST'])
def run_job():
    data = request.get_json()
    job_id = data.get('jobId')
    pipeline_id = data.get('pipelineId')

    if not job_id or not pipeline_id:
        return jsonify({'error': 'Missing jobId or pipelineId'}), 400

    job = Job.query.get(job_id)
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
def get_jobs():
    jobs = Job.query.all()
    return jsonify([job.to_dict() for job in jobs])
