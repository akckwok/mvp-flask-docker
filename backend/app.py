import os
from flask import Flask, send_from_directory
from . import pipeline_manager
from .config import UPLOADS_DIR, BASE_DIR
from .views import api

from . import db

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, static_folder=None)

    # --- Configuration ---
    # Load config from .config file
    app.config.from_pyfile('config.py')

    # --- Initialize Extensions ---
    db.init_app(app)

    # --- Create Directories ---
    # Ensure the uploads directory exists
    uploads_path = os.path.join(BASE_DIR, UPLOADS_DIR)
    if not os.path.exists(uploads_path):
        os.makedirs(uploads_path)

    # --- Discover Pipelines ---
    print("--- Initializing Pipelines ---")
    available_pipelines = pipeline_manager.discover_pipelines()
    if not available_pipelines:
        print("Warning: No pipelines found. Check the 'pipelines' directory.")
    else:
        print(f"Found {len(available_pipelines)} pipelines: {[p['name'] for p in available_pipelines]}")

    # Store pipelines in the app config for access in blueprints
    app.config['AVAILABLE_PIPELINES'] = available_pipelines

    # --- Register Blueprints ---
    app.register_blueprint(api, url_prefix='/api')

    # --- Create Database Tables ---
    with app.app_context():
        db.create_all()

    # --- Static File Serving ---
    # In a production environment, the frontend is served from the 'dist' directory.
    dist_dir = os.path.join(BASE_DIR, 'dashboard-ui', 'dist')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_spa(path):
        if path != "" and os.path.exists(os.path.join(dist_dir, path)):
            return send_from_directory(dist_dir, path)
        else:
            return send_from_directory(dist_dir, 'index.html')

    return app
