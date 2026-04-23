import unittest
from omni_mindnote_engine import OmniMindnoteEngine
from omni_comp_tech_list_engine import OmniCompTechListEngine
from omni_nge2_engine import OmniNGE2Engine
from omni_integration_test_engine import OmniIntegrationTestEngine
from omni_disaster_response_engine import OmniDisasterResponseEngine

class TestBatch34Integration(unittest.TestCase):
    def test_mindnote_engine(self):
        engine = OmniMindnoteEngine()
        # Engine expects a list of string blocks, not a single string
        blocks = ["Hello world from OMNI.", "OMNI is great."]
        res = engine.analyze_document(blocks)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["total_blocks"], 2)
        self.assertTrue(res["value"]["total_characters"] > 0)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_comp_tech_list_engine(self):
        engine = OmniCompTechListEngine()
        stack = {
            "frontend": ["react", "tailwind"],
            "backend": ["fastapi", "django"]
        }
        res = engine.evaluate_tech_stack(stack)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["total_components"], 4)
        self.assertTrue(res["value"]["architectural_density_coefficient"] > 0)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_nge2_engine(self):
        engine = OmniNGE2Engine()
        # Engine expects a single dict with spatial boundaries
        bounds = {"left": -10, "right": 10, "bottom": -10, "top": 10, "near": 0.1, "far": 100}
        res = engine.compute_orthographic_matrix(bounds)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(len(res["value"]["orthographic_projection"]), 4)
        self.assertTrue(res["value"]["volumetric_volume"] > 0)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_integration_test_engine(self):
        engine = OmniIntegrationTestEngine()
        graph = {
            "A": ["B", "C"],
            "B": ["D"],
            "C": ["D"],
            "D": []
        }
        res = engine.calculate_path_coverage(graph, "A")
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["paths_discovered"], 2)
        self.assertAlmostEqual(res["value"]["deterministic_coverage_ratio"], 1.0)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_disaster_response_engine(self):
        engine = OmniDisasterResponseEngine()
        # Engine expects lists of dicts with x,y keys, not tuples
        incidents = [
            {"x": 3, "y": 4, "severity": 10},
            {"x": 0, "y": 0, "severity": 2}
        ]
        resources = [
            {"x": 0, "y": 0},
            {"x": 5, "y": 5}
        ]
        res = engine.optimize_resource_distribution(incidents, resources)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["allocations_completed"], 2)
        self.assertEqual(res["value"]["unresolved_incidents"], 0)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

if __name__ == '__main__':
    unittest.main()
