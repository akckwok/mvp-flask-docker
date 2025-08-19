from datetime import datetime
import json
from . import db

class Job(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    _files = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='uploaded')
    pipeline = db.Column(db.String(50), nullable=True)
    container_id = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

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
