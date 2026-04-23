"""
Integration Test Suite for OMNI Semester 10 Batch 44
Canonical migration from sem10_batch44_integration_tests.py
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import unittest
from src.compute.python_core.omni_dalhousie_sdc_engine import OmniDalhousieSDCEngine
from src.compute.python_core.omni_calculator_app_engine import OmniCalculatorAppEngine
from src.compute.python_core.omni_adhd_wordsearch_engine import OmniADHDWordSearchEngine
from src.compute.python_core.omni_software_product_management_engine import OmniSoftwareProductManagementEngine
from src.compute.python_core.omni_code_auditor_engine import OmniCodeAuditorEngine

class TestBatch44Integration(unittest.TestCase):
    def test_dalhousie_sdc(self):
        engine = OmniDalhousieSDCEngine()
        modules = [{"concept_depth": 5.0, "assignment_load": 10.0}]
        # net_concept_depth = 5.0 * 1.61803 = 8.09015
        # aggregate_assignment_load = 10.0
        # density = (8.09015 / 10.0) * 3.14159 = 2.54159...
        res = engine.compute_academic_density_bounds(modules)
        self.assertEqual(res["status"], "success")
        self.assertAlmostEqual(res["value"]["net_concept_depth"], 8.09015, places=4)
        self.assertEqual(res["value"]["aggregate_assignment_load"], 10.0)
        self.assertTrue(res["value"]["academic_density_metric"] > 0)

    def test_calculator_app(self):
        engine = OmniCalculatorAppEngine()
        calcs = [{"operator_complexity": 8.0, "input_vector_size": 2.0}]
        # comp = 8.0
        # size = 2.0 * 2.71828 = 5.43656
        # vel = (8.0 / 5.43656) * 1.4142 = 2.081...
        res = engine.evaluate_operational_velocity(calcs)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["total_complexity_mass"], 8.0)
        self.assertAlmostEqual(res["value"]["aggregate_input_scaling"], 5.43656, places=4)
        self.assertTrue(res["value"]["velocity_vector_magnitude"] > 0)

    def test_adhd_wordsearch(self):
        engine = OmniADHDWordSearchEngine()
        sessions = [{"attention_span": 10.0, "distraction_index": 2.0}]
        res = engine.evaluate_cognitive_focus_bounds(sessions)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["value"]["aggregate_focus_matrix"] > 0)
        self.assertTrue(res["value"]["geometric_focus_limit"] > 0)

    def test_software_product_management(self):
        engine = OmniSoftwareProductManagementEngine()
        sprints = [{"story_points": 20.0, "cycle_time": 5.0}]
        # velocity = (20.0 * pi) / 5.0 = 12.566...
        res = engine.map_agile_velocity_bounds(sprints)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["value"]["aggregate_velocity_topology"] > 0)
        self.assertTrue(res["value"]["velocity_limit_scale"] > 0)

    def test_code_auditor(self):
        engine = OmniCodeAuditorEngine()
        nodes = [{"loc_volume": 1000.0, "vulnerability_weight": 5.0}]
        # loc = 1000.0
        # vulns = 5.0 * 2.048 = 10.24
        # ratio = 100.0 - ((10.24 / 1000.0) * 100.0) = 100.0 - 1.024 = 98.976
        res = engine.structural_compliance_matrix(nodes)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["aggregate_codebase_volume"], 1000.0)
        self.assertAlmostEqual(res["value"]["cumulative_security_mass"], 10.24, places=2)
        self.assertAlmostEqual(res["value"]["structural_compliance_ratio"], 98.976, places=3)

