import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from omni_kidi_age_calculator_engine import OmniKidiAgeCalculatorEngine
from omni_ios_roadmap_engine import OmniIOSRoadmapEngine
from omni_awesome_windows_engine import OmniAwesomeWindowsEngine
from omni_bounswe_group5_engine import OmniBounsweGroup5Engine
from omni_mgm_grand_onion_tor_engine import OmniMgmGrandOnionTorEngine

class TestBatch32Integration(unittest.TestCase):
    
    def test_kidi_age_calculator_engine(self):
        engine = OmniKidiAgeCalculatorEngine()
        # Test diff between 2000-01-01 and 2024-06-15
        res = engine.calculate_exact_duration("2000-01-01", "2024-06-15")
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["years"], 24)
        self.assertEqual(res["value"]["months"], 5)
        self.assertEqual(res["value"]["days"], 14)
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")
        
    def test_ios_roadmap_engine(self):
        engine = OmniIOSRoadmapEngine()
        res = engine.verify_learning_path(["swift_basics", "swift_oop"], "uikit_fundamentals")
        self.assertEqual(res["status"], "ok")
        self.assertTrue(res["value"]["is_unlocked"])
        
        res = engine.verify_learning_path(["swift_basics"], "core_data")
        self.assertEqual(res["status"], "ok")
        self.assertFalse(res["value"]["is_unlocked"])
        self.assertIn("uikit_fundamentals", res["value"]["missing_prerequisites"])

        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_awesome_windows_engine(self):
        engine = OmniAwesomeWindowsEngine()
        md = "* [ToolA](http://t.co) - A tool\n* [ToolB](http://a.co) - B tool"
        res = engine.parse_tools_markdown(md)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["extracted_count"], 2)
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_bounswe_group5_engine(self):
        engine = OmniBounsweGroup5Engine()
        files = ["package.json", "src/index.ts", "test/test.ts", "README.md", "tsconfig.json"]
        res = engine.audit_project_structure(files)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["compliance_score"], 1.0)
        self.assertTrue(res["value"]["is_compliant"])
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_mgm_grand_onion_tor_engine(self):
        engine = OmniMgmGrandOnionTorEngine()
        config = [
            "HiddenServiceDir /var/lib/tor/hs",
            "HiddenServicePort 80 127.0.0.1:80",
            "SocksPort 127.0.0.1:9050"
        ]
        res = engine.validate_torrc(config)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["hidden_services"], 1)
        self.assertTrue(res["value"]["is_secure"])
        self.assertEqual(len(res["value"]["issues"]), 0)
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

if __name__ == '__main__':
    unittest.main()
