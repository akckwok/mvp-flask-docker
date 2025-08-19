import os
import json
import subprocess

def discover_pipelines():
    """
    Discovers pipelines by scanning the 'pipelines' directory.
    Each pipeline is a subdirectory containing a 'manifest.json' file.
    """
    pipelines = []
    pipeline_dir = './pipelines'
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

def build_pipelines(pipelines):
    """
    Builds Docker images for the given pipelines using sudo.
    """
    for pipeline in pipelines:
        pipeline_id = pipeline['id']
        image_name = pipeline.get('image_name', f"{pipeline_id}-image")
        pipeline_path = os.path.join('./pipelines', pipeline_id)

        print(f"Building image '{image_name}' from '{pipeline_path}'...")
        try:
            # Added 'sudo' to the command
            subprocess.run(
                ['sudo', 'docker', 'build', '-t', image_name, pipeline_path],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"Image '{image_name}' built successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error building Docker image for '{pipeline_id}'. Please ensure Docker is running.")
            print(f"Stderr:\n{e.stderr}")
            raise
        except FileNotFoundError:
            print("Error: 'docker' or 'sudo' command not found. Please ensure they are installed and in your PATH.")
            raise

def run_pipeline(pipeline, job_id, filenames):
    """
    MOCK: Simulates running a pipeline without Docker for testing purposes.
    """
    print(f"--- MOCK RUN: Pipeline '{pipeline['id']}' for job '{job_id}' ---")
    print(f"--- MOCK RUN: Input files: {filenames} ---")

    # Create a mock process object with a pid, as server.py expects it.
    class MockProcess:
        def __init__(self):
            self.pid = 12345 # A dummy PID

    print(f"Pipeline '{pipeline['id']}' for job '{job_id}' (MOCK) started with PID: 12345")
    return MockProcess()
