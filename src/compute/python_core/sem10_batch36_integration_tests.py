import unittest
from omni_vscode_shortcuts_engine import OmniVscodeShortcutsEngine
from omni_git_analyzer_engine import OmniGitAnalyzerEngine
from omni_learnlang_engine import OmniLearnlangEngine
from omni_gam3du_engine import OmniGam3duEngine
from omni_apis_engine import OmniAPIsEngine

class TestBatch36Integration(unittest.TestCase):
    def test_vscode_shortcuts_engine(self):
        engine = OmniVscodeShortcutsEngine()
        shortcuts = ["ctrl+c", "ctrl+v", "ctrl+c", "alt+shift+k"]
        res = engine.calculate_shortcut_collisions(shortcuts)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["collisions_detected"], 1)
        self.assertEqual(res["value"]["modifier_distribution"]["ctrl"], 3)
        self.assertEqual(res["value"]["modifier_distribution"]["alt"], 1)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_git_analyzer_engine(self):
        engine = OmniGitAnalyzerEngine()
        edges = [("A", "B"), ("B", "C"), ("C", "A"), ("D", "E")] # Cycle A-B-C, disconnected D-E
        res = engine.analyze_commit_topology(edges)
        self.assertEqual(res["status"], "ok")
        self.assertTrue(res["value"]["cycles_detected"])
        self.assertTrue(res["value"]["disconnected_branches_detected"])
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_learnlang_engine(self):
        engine = OmniLearnlangEngine()
        grammar = ["print", "if", "else"]
        tokens = ["print", "elif", "else"]
        res = engine.compute_syntax_divergence(grammar, tokens)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["exact_matches"], 2)
        # Edit distance from 'elif' to ['print', 'if', 'else'], min is to 'esle' -> e,l,s,e / e,l,i,f ... to 'if' -> i,f / e,l,i,f -> distance 2
        self.assertEqual(res["value"]["cumulative_divergence"], 2)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_gam3du_engine(self):
        engine = OmniGam3duEngine()
        vertices = [[1, 1, 1], [0, 0, 0]]
        # Translation matrix +2x, +3y
        matrix = [
            [1, 0, 0, 2],
            [0, 1, 0, 3],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]
        res = engine.compute_affine_transforms(vertices, matrix)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["transformed_matrix"][0], [3.0, 4.0, 1.0])
        self.assertEqual(res["value"]["transformed_matrix"][1], [2.0, 3.0, 0.0])
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_apis_engine(self):
        engine = OmniAPIsEngine()
        schema = {
            "user": {
                "id": "uuid",
                "roles": ["admin", "user"]
            }
        }
        res = engine.evaluate_schema_density(schema)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["topological_depth"], 3)
        self.assertEqual(res["value"]["total_keys_allocated"], 3) # user, id, roles
        self.assertEqual(res["value"]["total_arrays_allocated"], 1)
        self.assertEqual(res["value"]["density_coefficient"], round(4 / 3, 4))
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

if __name__ == '__main__':
    unittest.main()
