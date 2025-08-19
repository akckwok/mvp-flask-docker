import os
from flask import Flask, send_from_directory
from . import pipeline_manager
from .config import UPLOADS_DIR, BASE_DIR
from .views import api

from . import db
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from .models import User

bcrypt = Bcrypt()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, static_folder=None)

    # --- Configuration ---
    # Load config from .config file
    app.config.from_pyfile('config.py')
    app.config['SECRET_KEY'] = 'a_super_secret_key' # CHANGE THIS!

    # --- Initialize Extensions ---
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

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
    # In a production environment, the frontend is served from the 'dashboard-ui' directory.
    ui_dir = os.path.join(BASE_DIR, 'dashboard-ui')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_spa(path):
        if path and os.path.exists(os.path.join(ui_dir, path)):
            return send_from_directory(ui_dir, path)

        if not current_user.is_authenticated:
            return send_from_directory(ui_dir, 'login.html')

        if path in ['login', 'register']:
             return send_from_directory(ui_dir, f'{path}.html')

        return send_from_directory(ui_dir, 'index.html')

    return app
