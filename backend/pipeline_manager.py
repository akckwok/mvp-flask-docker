import os
import json
import docker
from flask import current_app
from .config import BASE_DIR, UPLOADS_DIR

def discover_pipelines(pipeline_dir=None):
    """
    Discovers pipelines by scanning a directory.
    Each pipeline is a subdirectory containing a 'manifest.json' file.
    """
    pipelines = []
    if pipeline_dir is None:
        pipeline_dir = os.path.join(BASE_DIR, 'pipelines')

    if not os.path.exists(pipeline_dir):
        return pipelines

    for pipeline_name in os.listdir(pipeline_dir):
        manifest_path = os.path.join(pipeline_dir, pipeline_name, 'manifest.json')
        if os.path.isfile(manifest_path):
            with open(manifest_path, 'r') as f:
                try:
                    manifest = json.load(f)
                    manifest['id'] = pipeline_name
                    pipelines.append(manifest)
                except json.JSONDecodeError:
                    print(f"Warning: Could not parse manifest for pipeline '{pipeline_name}'.")
    return pipelines

def run_pipeline(pipeline, job_id, filenames):
    """
    Runs a pipeline in a Docker container.
    """
    if current_app.config.get('TESTING'):
        # In testing mode, create dummy files to avoid issues with real data
        host_uploads_path = os.path.join(BASE_DIR, UPLOADS_DIR)
        if not os.path.exists(host_uploads_path):
            os.makedirs(host_uploads_path)

        for filename in filenames:
            filepath = os.path.join(host_uploads_path, filename)
            with open(filepath, 'w') as f:
                f.write(f"This is a dummy file for {filename}.")

    client = docker.from_env()
    image_name = pipeline.get('image_name', f"{pipeline['id']}-image")

    # In a real app, you should handle image not found errors
    try:
        client.images.get(image_name)
    except docker.errors.ImageNotFound:
        print(f"Error: Docker image '{image_name}' not found.")
        # For this project, we assume images are pre-built.
        # You could add a call to build_pipelines here if you want to build on the fly.
        return None

    # Path to the uploads directory on the host
    host_uploads_path = os.path.join(BASE_DIR, UPLOADS_DIR)

    # The container will have a corresponding /uploads volume
    container_uploads_path = '/uploads'

    # Create the volume mapping
    volumes = {
        host_uploads_path: {'bind': container_uploads_path, 'mode': 'rw'}
    }

    # The command to run in the container will be the list of filenames
    # prefixed by their path in the container.
    container_filepaths = [os.path.join(container_uploads_path, f) for f in filenames]

    try:
        container = client.containers.run(
            image_name,
            command=container_filepaths,
            volumes=volumes,
            detach=True  # Run in the background
        )
        print(f"Started container {container.id} for job {job_id}")
        # We return the container object itself. The view can get the ID.
        return container
    except docker.errors.ContainerError as e:
        print(f"Error running container for job {job_id}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while running the pipeline: {e}")
        return None
