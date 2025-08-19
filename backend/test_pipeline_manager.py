import unittest
import os
import json
import tempfile
import shutil
from backend.app import create_app
from backend.models import db, Job
from backend.pipeline_manager import discover_pipelines

class TestPipelineManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.pipelines_dir = os.path.join(self.test_dir, 'pipelines')
        os.makedirs(self.pipelines_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_discover_pipelines_success(self):
        # Create a valid pipeline
        pipeline1_dir = os.path.join(self.pipelines_dir, 'pipeline1')
        os.makedirs(pipeline1_dir)
        manifest1 = {"name": "Pipeline 1"}
        with open(os.path.join(pipeline1_dir, 'manifest.json'), 'w') as f:
            json.dump(manifest1, f)

        pipelines = discover_pipelines(pipeline_dir=self.pipelines_dir)
        self.assertEqual(len(pipelines), 1)
        self.assertEqual(pipelines[0]['name'], 'Pipeline 1')

    def test_discover_pipelines_no_manifest(self):
        # Create a directory without a manifest
        os.makedirs(os.path.join(self.pipelines_dir, 'pipeline_no_manifest'))
        pipelines = discover_pipelines(pipeline_dir=self.pipelines_dir)
        self.assertEqual(len(pipelines), 0)

    def test_discover_pipelines_bad_manifest(self):
        # Create a pipeline with a malformed manifest
        pipeline_bad_dir = os.path.join(self.pipelines_dir, 'pipeline_bad')
        os.makedirs(pipeline_bad_dir)
        with open(os.path.join(pipeline_bad_dir, 'manifest.json'), 'w') as f:
            f.write("{'name': 'Bad JSON',}") # Invalid JSON
        pipelines = discover_pipelines(pipeline_dir=self.pipelines_dir)
        self.assertEqual(len(pipelines), 0)


class TestApi(unittest.TestCase):
    def setUp(self):
        """Set up a test client and initialize the database."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Tear down the database."""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_get_jobs(self):
        """Test the /api/jobs endpoint."""
        with self.app.app_context():
            job = Job(id='test-job', files=[{'filename': 'test.txt'}])
            db.session.add(job)
            db.session.commit()

        response = self.client.get('/api/jobs')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], 'test-job')

if __name__ == '__main__':
    unittest.main()
