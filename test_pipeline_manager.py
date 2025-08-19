import unittest
import os
import json
import tempfile
import shutil
from pipeline_manager import discover_pipelines

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
        manifest1 = {
            "name": "Pipeline 1",
            "description": "A test pipeline.",
            "inputs": [{"name": "input1", "type": "file"}],
            "outputs": [{"name": "output1", "type": "file"}]
        }
        with open(os.path.join(pipeline1_dir, 'manifest.json'), 'w') as f:
            json.dump(manifest1, f)

        # Create another valid pipeline
        pipeline2_dir = os.path.join(self.pipelines_dir, 'pipeline2')
        os.makedirs(pipeline2_dir)
        manifest2 = {
            "name": "Pipeline 2",
            "description": "Another test pipeline."
        }
        with open(os.path.join(pipeline2_dir, 'manifest.json'), 'w') as f:
            json.dump(manifest2, f)

        # Temporarily change to the test directory to run discover_pipelines
        original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        try:
            pipelines = discover_pipelines()
            self.assertEqual(len(pipelines), 2)

            p1 = next((p for p in pipelines if p['id'] == 'pipeline1'), None)
            self.assertIsNotNone(p1)
            self.assertEqual(p1['name'], 'Pipeline 1')
            self.assertIn('outputs', p1)

            p2 = next((p for p in pipelines if p['id'] == 'pipeline2'), None)
            self.assertIsNotNone(p2)
            self.assertEqual(p2['name'], 'Pipeline 2')
            self.assertNotIn('outputs', p2)

        finally:
            os.chdir(original_cwd)

    def test_discover_pipelines_no_manifest(self):
        # Create a directory without a manifest
        os.makedirs(os.path.join(self.pipelines_dir, 'pipeline_no_manifest'))

        original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        try:
            pipelines = discover_pipelines()
            self.assertEqual(len(pipelines), 0)
        finally:
            os.chdir(original_cwd)

    def test_discover_pipelines_bad_manifest(self):
        # Create a pipeline with a malformed manifest
        pipeline_bad_dir = os.path.join(self.pipelines_dir, 'pipeline_bad')
        os.makedirs(pipeline_bad_dir)
        with open(os.path.join(pipeline_bad_dir, 'manifest.json'), 'w') as f:
            f.write("{'name': 'Bad JSON',}") # Invalid JSON

        original_cwd = os.getcwd()
        os.chdir(self.test_dir)
        try:
            pipelines = discover_pipelines()
            self.assertEqual(len(pipelines), 0)
        finally:
            os.chdir(original_cwd)

if __name__ == '__main__':
    unittest.main()
