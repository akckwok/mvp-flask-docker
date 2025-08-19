import json
from datetime import date
from backend.app import create_app, db
from backend.models import User, Project, DataSubmission
from backend.extensions import bcrypt

app = create_app()
with app.app_context():
    # Create all database tables
    db.create_all()

    # Check if the test user already exists
    if not User.query.filter_by(username='testuser').first():
        print("Seeding database with test data...")

        # 1. Create a test user
        hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
        test_user = User(
            username='testuser',
            full_name='Test User',
            email='test@example.com',
            password_hash=hashed_password
        )
        db.session.add(test_user)

        # 2. Create a test project
        test_project = Project(
            id='TEST-PROJ-2023',
            project_name='Test Project 2023',
            project_lead='Dr. Test',
            start_date=date(2023, 1, 1),
            status='In Progress',
            description='A test project for demonstration purposes.'
        )
        db.session.add(test_project)
        db.session.commit() # Commit user and project to get their IDs

        # 3. Create a test data submission
        test_submission = DataSubmission(
            name='Initial Test Submission',
            description='Raw data from the first batch of samples.',
            project_id=test_project.id,
            sample_ids='sample1, sample2, sample3',
            extraction_date=date(2023, 3, 15),
            extracted_by='Test User',
            extraction_method='DNeasy PowerSoil Pro Kit',
            sequencing_method='Whole Genome Shotgun',
            submitted_to='Test Facility',
            submission_date=date.today(),
            user_id=test_user.id,
            uploaded_files=json.dumps([
                {'original_filename': 'test_data.fastq.gz', 'filepath': '/uploads/dummy_test_data.fastq.gz'},
                {'original_filename': 'provenance_email.eml', 'filepath': '/uploads/dummy_provenance_email.eml'}
            ])
        )
        db.session.add(test_submission)

        # Commit all the changes
        db.session.commit()
        print("Database seeded successfully.")
    else:
        print("Test data already exists. Skipping seeding.")

print("Database initialization complete.")
