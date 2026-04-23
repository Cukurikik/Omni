import unittest
from omni_care_iomt_engine import OmniCareIoMTEngine
from omni_fish_competition_engine import OmniFishCompetitionEngine
from omni_packaged_engine import OmniPackagEDEngine
from omni_garage_experiments_engine import OmniGarageExperimentsEngine
from omni_neit_language_engine import OmniNeitLanguageEngine

class TestBatch43Integration(unittest.TestCase):
    def test_care_iomt(self):
        engine = OmniCareIoMTEngine()
        grid = [{"signal_strength": 9.0, "latency_ms": 10.0}]
        # latency = 10.5
        # fidelity = 0.9
        # index = 0.9 * 2.718 = 2.4462
        res = engine.compute_sensor_network_topology(grid)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["aggregate_latency_mass"], 10.5)
        self.assertAlmostEqual(res["value"]["signal_fidelity_index"], 2.4462, places=4)

    def test_fish_competition(self):
        engine = OmniFishCompetitionEngine()
        agents = [{"agent_score": 10.0, "moves_count": 5.0}]
        # density = 2.0
        # efficiency = 2.0 * 1.618 = 3.236
        res = engine.compute_geometric_competition_bounds(agents)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["geometric_competition_density"], 2.0)
        self.assertAlmostEqual(res["value"]["agent_efficiency_limit"], 3.236, places=3)

    def test_packaged(self):
        engine = OmniPackagEDEngine()
        vectors = [{"x_delta": 3.0, "y_delta": 4.0, "z_delta": 0.0}]
        # span = sqrt(9+16+0) = 5.0
        # boundary = 5.0 / pi = 1.5915...
        res = engine.calculate_drawing_geometric_scale(vectors)
        self.assertEqual(res["status"], "success")
        self.assertAlmostEqual(res["value"]["aggregate_geometric_span"], 5.0, places=4)
        self.assertTrue(res["value"]["dimensional_boundary_index"] > 0)

    def test_garage_experiments(self):
        engine = OmniGarageExperimentsEngine()
        cells = [{"cell_complexity": 8.0, "execution_time": 2.2}]
        # mass = 9.6
        # time = 2.2
        # intensity = (9.6 / 2.2) * 0.85 = 3.709
        res = engine.compute_heuristic_flow_bounds(cells)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["cognitive_flow_mass"], 9.6)
        self.assertEqual(res["value"]["total_heuristic_execution"], 2.2)
        self.assertAlmostEqual(res["value"]["heuristic_intensity_bounds"], 3.709, places=3)

    def test_neit_language(self):
        engine = OmniNeitLanguageEngine()
        ast_layers = [{"ast_nodes": 500.0, "syntax_depth": 15.0}]
        # vol = 750.0. depth = 30.0.
        # fidelity = (750.0 / 30.0) * 1.024 = 25.6
        res = engine.calculate_ast_synthesis_matrix(ast_layers)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["ast_net_volume"], 750.0)
        self.assertEqual(res["value"]["syntax_tree_depth"], 30.0)
        self.assertAlmostEqual(res["value"]["compilation_fidelity_limit"], 25.6, places=3)

if __name__ == '__main__':
    unittest.main()
