"""
Integration Test Suite for OMNI Semester 10 Batch 31
Canonical migration from sem10_batch31_integration_tests.py
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import unittest


from src.compute.python_core.omni_hanoi_rainbow_engine import OmniHanoiRainbowEngine
from src.compute.python_core.omni_pyexe_builder_engine import OmniPyExeBuilderEngine
from src.compute.python_core.omni_object_detection_engine import OmniObjectDetectionEngine
from src.compute.python_core.omni_github_actions_prep_engine import OmniGithubActionsPrepEngine
from src.compute.python_core.omni_mh_makefile_engine import OmniMhMakefileEngine

class TestBatch31Integration(unittest.TestCase):
    
    def test_hanoi_rainbow_engine(self):
        engine = OmniHanoiRainbowEngine()
        engine.register_agent_skill("agent_A", "code", 5.0)
        task = [{"agent_id": "agent_A", "skill": "code", "complexity": 2.5}]
        res = engine.execute_workflow("WF-1", task)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["workflow_id"], "WF-1")
        self.assertEqual(res["value"]["total_cost"], 0.5)
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")
        
    def test_pyexe_builder_engine(self):
        engine = OmniPyExeBuilderEngine()
        code = "import os\ndef test():\n    pass\n"
        res = engine.compile_executable("app", code)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["metrics"]["imports"], 1)
        self.assertEqual(res["value"]["metrics"]["functions"], 1)
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")
        
    def test_object_detection_engine(self):
        engine = OmniObjectDetectionEngine()
        signal = [0.1, 0.2, 0.9, 0.4, 0.1, 0.8, 0.2]
        res = engine.detect_peaks(signal, threshold=0.5, window_size=1)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["count"], 2)
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")
        
    def test_github_actions_prep_engine(self):
        engine = OmniGithubActionsPrepEngine()
        pipeline = {
            "name": "CI",
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "steps": [{"run": "make build"}, {"uses": "actions/checkout"}]
                }
            }
        }
        res = engine.validate_pipeline(pipeline)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["overall_confidence"], 1.0)
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_mh_makefile_engine(self):
        engine = OmniMhMakefileEngine()
        makefile = "build: ## Build the app\n\tgo build\ntest: ## Run tests\n\tgo test"
        res = engine.parse_makefile(makefile)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["targets_found"], 2)
        self.assertEqual(res["value"]["docs"]["build"], "Build the app")
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

