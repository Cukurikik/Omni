import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from omni_vscode_shortcuts_engine import OmniVSCodeShortcutsEngine
from omni_git_analyzer_engine import OmniGitAnalyzerEngine
from omni_learnlang_engine import OmniLearnlangEngine
from omni_gam3du_engine import OmniGam3duEngine
from omni_awesome_apis_engine import OmniAwesomeAPIsEngine

class TestBatch33Integration(unittest.TestCase):
    
    def test_vscode_shortcuts_engine(self):
        engine = OmniVSCodeShortcutsEngine()
        res = engine.calculate_shortcut_collisions([
            "Ctrl+Shift+P",
            "ctrl+shift+p",
            "Alt+F4"
        ])
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["total_processed"], 3)
        self.assertEqual(res["value"]["collisions_detected"], 1)
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")
        
    def test_git_analyzer_engine(self):
        engine = OmniGitAnalyzerEngine()
        commits = [
            {"author": "alice", "message": "init", "changes": 10},
            {"author": "bob", "message": "feature", "changes": 50},
            {"author": "alice", "message": "fix", "changes": 5}
        ]
        res = engine.analyze_commit_topology(commits)
        self.assertEqual(res["status"], "ok")
        self.assertTrue(res["value"]["DAG_integrity"])

        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_learnlang_engine(self):
        engine = OmniLearnlangEngine()
        base_grammar = ["fn", "let", "if", "else", "return"]
        sample_tokens = ["fn", "let", "while", "for"]
        res = engine.compute_syntax_divergence(base_grammar, sample_tokens)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["exact_matches"], 2)
        self.assertEqual(res["value"]["coverage_ratio"], 0.5)
        self.assertTrue(res["value"]["cumulative_divergence"] > 0)
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_gam3du_engine(self):
        engine = OmniGam3duEngine()
        vertices = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        # Identity matrix — no transformation
        transform = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]
        res = engine.compute_affine_transforms(vertices, transform)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["vertex_count"], 3)
        self.assertEqual(res["value"]["transformed_matrix"][0], [1.0, 0.0, 0.0])
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_awesome_apis_engine(self):
        engine = OmniAwesomeAPIsEngine()
        apis = [
            {"name": "Cat Facts", "https": True, "cors": "yes", "category": "Animals"},
            {"name": "Dog Facts", "https": False, "cors": "no", "category": "Animals"},
            {"name": "Weather", "https": True, "cors": "unknown", "category": "Science"}
        ]
        res = engine.analyze_api_manifest(apis)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["secure_https_ratio"], 0.6667)
        self.assertEqual(res["value"]["cors_enabled_ratio"], 0.3333)
        self.assertFalse(res["value"]["is_production_ready"])
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

if __name__ == '__main__':
    unittest.main()
