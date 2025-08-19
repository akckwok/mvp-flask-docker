import os

# Directory for storing uploaded files
UPLOADS_DIR = 'uploads'

# Absolute path to the project root
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Database configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
