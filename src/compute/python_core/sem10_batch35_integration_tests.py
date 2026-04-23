import unittest
from omni_dh_tech_engine import OmniDHTechEngine
from omni_breakbase_frontend_engine import OmniBreakbaseFrontendEngine
from omni_technical_hub_engine import OmniTechnicalHubEngine
from omni_kwaliteitsaanpak_engine import OmniKwaliteitsaanpakEngine
from omni_sboannotator_engine import OmniSBOannotatorEngine

class TestBatch35Integration(unittest.TestCase):
    def test_dh_tech_engine(self):
        engine = OmniDHTechEngine()
        dom = {
            "tag": "div",
            "children": [
                {"tag": "p", "children": []},
                {"tag": "span", "children": [{"tag": "a", "children": []}]}
            ]
        }
        res = engine.analyze_dom_topology(dom)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["max_depth"], 3)
        self.assertEqual(res["value"]["tag_distribution"]["a"], 1)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_breakbase_frontend_engine(self):
        engine = OmniBreakbaseFrontendEngine()
        components = {
            "Header": ["Logo", "Nav"],
            "Logo": [],
            "Nav": ["Link"],
            "Link": ["Header"] # cycle
        }
        res = engine.resolve_component_graph(components)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["circular_dependencies_detected"], 1)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_technical_hub_engine(self):
        engine = OmniTechnicalHubEngine()
        article = "Technical management is management."
        res = engine.extract_term_frequency(article)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["word_count"], 4)
        self.assertEqual(res["value"]["term_frequencies"]["management"], 0.5)
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_kwaliteitsaanpak_engine(self):
        engine = OmniKwaliteitsaanpakEngine()
        ast = ["IF", "ASSIGN", "WHILE", "MAGIC_NUMBER"]
        res = engine.assess_code_quality(ast)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["cyclomatic_complexity"], 3)
        self.assertEqual(res["value"]["anti_patterns_found"], 1)
        self.assertEqual(res["value"]["quality_score"], 84) # 100 - 6 - 10
        self.assertTrue(res["value"]["passed"])
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_sboannotator_engine(self):
        engine = OmniSBOannotatorEngine()
        chars = ["kinase", "phosphoryl"]
        res = engine.annotate_biological_entity("EnzymeX", chars)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["value"]["entity"], "EnzymeX")
        self.assertTrue(res["value"]["assigned_sbo_term"].startswith("SBO:"))
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

if __name__ == '__main__':
    unittest.main()
