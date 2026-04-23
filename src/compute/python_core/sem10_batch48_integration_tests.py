import unittest
from omni_amazon_finance_data_engine import OmniAmazonFinanceDataEngine
from omni_pypi_research_data_engine import OmniPyPIResearchDataEngine
from omni_cybersecurity_software_engine import OmniCybersecuritySoftwareEngine
from omni_ncu_sep_engine import OmniNCUSEPEngine
from omni_bugtrons_con_engine import OmniBugtronsConEngine

class TestBatch48Integration(unittest.TestCase):
    def test_amazon_finance(self):
        engine = OmniAmazonFinanceDataEngine()
        data = [{"rd_spend": 100000.0, "marketing_spend": 50000.0}]
        res = engine.evaluate_financial_normalization(data)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["value"]["aggregate_log_normalization"] > 0)
        
    def test_pypi_research(self):
        engine = OmniPyPIResearchDataEngine()
        nodes = [{"downloads": 50000.0, "licenses": 1.0}]
        res = engine.calculate_research_index_geometry(nodes)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["value"]["aggregate_research_geometry"] > 0)

    def test_cybersecurity_software(self):
        engine = OmniCybersecuritySoftwareEngine()
        vulns = [{"cvss_score": 9.8, "mitigation_depth": 3.0}]
        res = engine.map_cybersecurity_boundaries(vulns)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["value"]["aggregate_defense_matrix"] > 0)

    def test_ncu_sep(self):
        engine = OmniNCUSEPEngine()
        metrics = [{"cyclomatic_complexity": 10.0, "test_coverage": 85.0}]
        res = engine.evaluate_software_engineering_practice(metrics)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["value"]["aggregate_practice_validation"] > 0)

    def test_bugtrons(self):
        engine = OmniBugtronsConEngine()
        tracks = [{"attendees": 500.0, "sessions": 10.0}]
        res = engine.map_roadmap_conference_topology(tracks)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["value"]["aggregate_roadmap_topology"] > 0)

if __name__ == '__main__':
    unittest.main()
