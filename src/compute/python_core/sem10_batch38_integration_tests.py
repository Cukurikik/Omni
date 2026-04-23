import unittest
from omni_go_start_engine import OmniGoStartEngine
from omni_vid_game_console_management_engine import OmniVidGameConsoleManagementEngine
from omni_hunger_games_search_engine import OmniHungerGamesSearchEngine
from omni_course_dev_engine import OmniCourseDevEngine
from omni_development_rules_engine import OmniDevelopmentRulesEngine

class TestBatch38Integration(unittest.TestCase):
    def test_go_start_engine(self):
        engine = OmniGoStartEngine()
        tokens = ["struct", "pointer", "map", "func", "goroutine"]
        res = engine.evaluate_go_concepts(tokens)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["total_tokens"], 5)
        # struct(7) * pointer(17) * map(13) * goroutine(2) + 0.5 (func)
        # 7*17 = 119
        # 119*13 = 1547
        # 1547*2 = 3094
        # 3094 + 0.5 = 3094.5
        self.assertEqual(res["value"]["structural_density"], 3095.0)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_vid_game_console_management_engine(self):
        engine = OmniVidGameConsoleManagementEngine()
        consoles = [{"name": "ps5", "stock": 10}, {"name": "xbox", "stock": 5}]
        demands = [{"id": 1, "quantity": 12}, {"id": 2, "quantity": 5}]
        res = engine.calculate_inventory_matrix(consoles, demands)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["total_consoles_stock"], 15)
        self.assertEqual(res["value"]["total_demand"], 17)
        self.assertEqual(res["value"]["unfulfilled_demand"], 2)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_hunger_games_search_engine(self):
        engine = OmniHungerGamesSearchEngine()
        res = engine.optimize_search_space(50, 10)
        self.assertEqual(res["status"], "ok")
        self.assertTrue("final_convergence_factor" in res["value"])
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_course_dev_engine(self):
        engine = OmniCourseDevEngine()
        modules = [
            {"name": "A", "dependencies": ["B"]},
            {"name": "B", "dependencies": ["C"]},
            {"name": "C", "dependencies": []}
        ]
        res = engine.calculate_pedagogical_topology(modules)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["max_curriculum_depth"], 3)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_development_rules_engine(self):
        engine = OmniDevelopmentRulesEngine()
        rule_set = {"solid": 10.0, "dry": 8.5, "kiss": 9.0}
        architecture_layers = ["ui", "domain", "system"]
        res = engine.analyze_compliance_topology(rule_set, architecture_layers)
        self.assertEqual(res["status"], "ok")
        self.assertTrue("ecosystem_compliance_factor" in res["value"])
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

if __name__ == '__main__':
    unittest.main()
