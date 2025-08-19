from datetime import datetime
import json
from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)

    jobs = db.relationship('Job', backref='user', lazy=True)

class Job(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    _files = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='uploaded')
    pipeline = db.Column(db.String(50), nullable=True)
    container_id = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def files(self):
        return json.loads(self._files)

    @files.setter
    def files(self, value):
        self._files = json.dumps(value)

    def to_dict(self):
        return {
            'id': self.id,
            'files': self.files,
            'status': self.status,
            'pipeline': self.pipeline,
            'created_at': self.created_at.isoformat()
        }


# Association table for the many-to-many relationship between LabMember and Skill
lab_member_skills = db.Table('lab_member_skills',
    db.Column('lab_member_id', db.Integer, db.ForeignKey('lab_member.id'), primary_key=True),
    db.Column('skill_id', db.Integer, db.ForeignKey('skill.id'), primary_key=True)
)


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<Skill {self.name}>'


class LabMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    projects = db.Column(db.Text, nullable=True)
    responsibilities = db.Column(db.Text, nullable=True)

    skills = db.relationship('Skill', secondary=lab_member_skills, lazy='subquery',
        backref=db.backref('lab_members', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'role': self.role,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'projects': self.projects,
            'responsibilities': self.responsibilities,
            'skills_str': ', '.join(skill.name for skill in self.skills)
        }


class Project(db.Model):
    id = db.Column(db.String(100), primary_key=True)
    project_name = db.Column(db.String(200), nullable=False)
    project_lead = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    sample_type = db.Column(db.String(200), nullable=True)
    sequencing_method = db.Column(db.String(200), nullable=True)
    year = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'project-name': self.project_name,
            'project-lead': self.project_lead,
            'year': self.start_date.year if self.start_date else None,
            'status': self.status,
            'sequencing-method': self.sequencing_method
        }


class DataSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.String(100), db.ForeignKey('project.id'), nullable=False)
    sample_ids = db.Column(db.Text, nullable=False)
    extraction_date = db.Column(db.Date, nullable=False)
    extracted_by = db.Column(db.String(120), nullable=False)
    extraction_method = db.Column(db.String(100), nullable=False)
    method_modifications = db.Column(db.Text, nullable=True)
    sequencing_method = db.Column(db.String(100), nullable=False)
    primers_used = db.Column(db.String(200), nullable=True)
    submitted_to = db.Column(db.String(120), nullable=False)
    submission_date = db.Column(db.Date, nullable=False)
    raw_data_file = db.Column(db.String(200), nullable=True)
    provenance_email = db.Column(db.String(200), nullable=True)

    project = db.relationship('Project', backref=db.backref('data_submissions', lazy=True))
