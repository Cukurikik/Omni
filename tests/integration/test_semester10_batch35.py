"""
Integration Test Suite for OMNI Semester 10 Batch 35
Canonical migration from sem10_batch35_integration_tests.py
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import unittest
from src.compute.python_core.omni_dh_tech_engine import OmniDHTechEngine
from src.compute.python_core.omni_breakbase_frontend_engine import OmniBreakbaseFrontendEngine
from src.compute.python_core.omni_technical_hub_engine import OmniTechnicalHubEngine
from src.compute.python_core.omni_kwaliteitsaanpak_engine import OmniKwaliteitsaanpakEngine
from src.compute.python_core.omni_sboannotator_engine import OmniSBOannotatorEngine

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

