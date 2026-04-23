import unittest
from omni_awesome_ruhr_it_jobs_engine import OmniAwesomeRuhrITJobsEngine
from omni_ohtu2017_engine import OmniOhtu2017Engine
from omni_georgetown_opim243_engine import OmniGeorgetownOPIM243Engine
from omni_covidfo_engine import OmniCovidfoEngine
from omni_growing_oos_engine import OmniGrowingOOSEngine

class TestBatch39Integration(unittest.TestCase):
    def test_ruhr_it_jobs_engine(self):
        engine = OmniAwesomeRuhrITJobsEngine()
        res = engine.compute_ruhr_hub_density([
            {"x": 51.5136, "y": 7.4653, "mass": 10.0} # exact match Dortmund -> distance 0
        ])
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["network_gravity"], 10.0) # 10 / (0 + 1)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_ohtu2017_engine(self):
        engine = OmniOhtu2017Engine()
        tasks = [{"complexity": 2.0, "priority": 6.0, "effort": 3.0}]
        res = engine.calculate_sprint_velocity_integral(tasks)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["total_capacity_volume"], 4.0)
        self.assertEqual(res["value"]["critical_path_length"], 4.0)
        self.assertEqual(res["value"]["agile_momentum_index"], 20.0)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_georgetown_opim243_engine(self):
        engine = OmniGeorgetownOPIM243Engine()
        nodes = [{"revenue_potential": 100.0, "cost_overhead": 50.0, "automation_factor": 2.0}]
        res = engine.compute_business_logic_matrix(nodes)
        self.assertEqual(res["status"], "success")
        # rev = 200, cost = 50 / 2.1 = 23.8095238
        # index = 200 / 23.8095238 = 8.4
        # scalar = 2.5
        # convergence = 8.4 * 2.5 = 21.0
        self.assertAlmostEqual(res["value"]["business_convergence_matrix"], 21.0, places=3)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_covidfo_engine(self):
        engine = OmniCovidfoEngine()
        params = {
            "S_0": 1000.0, "I_0": 10.0, "R_0": 0.0,
            "beta_transmission": 0.0, "gamma_recovery": 0.1, "steps": 1
        }
        res = engine.calculate_epidemiological_limit(params)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["final_I"], 9.0)
        self.assertEqual(res["value"]["final_R"], 1.0)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_growing_oos_engine(self):
        engine = OmniGrowingOOSEngine()
        interfaces = [{"methods": 5, "dependencies": 2, "is_polymorphic": True}]
        res = engine.compute_object_graph_density(interfaces)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["total_methods"], 5)
        # 25 / 11 = 2.2727... * 1.2 = 2.7272...
        self.assertAlmostEqual(res["value"]["structural_index"], 2.7273, places=3)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

if __name__ == '__main__':
    unittest.main()
