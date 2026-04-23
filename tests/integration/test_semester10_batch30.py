"""
Integration Test Suite for OMNI Semester 10 Batch 30
Canonical migration from sem10_batch30_integration_tests.py
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import unittest


from src.compute.python_core.omni_restaurant_management_engine import OmniRestaurantManagementEngine
from src.compute.python_core.omni_skills_web_dev_engine import OmniSkillsWebDevEngine
from src.compute.python_core.omni_erp_saas_engine import OmniErpSaasEngine
from src.compute.python_core.omni_oxygen_project_engine import OmniOxygenProjectEngine
from src.compute.python_core.omni_debithub_banking_engine import OmniDebithubBankingEngine

class TestBatch30Integration(unittest.TestCase):
    
    def test_restaurant_engine(self):
        engine = OmniRestaurantManagementEngine()
        engine.add_menu_item("B1", "Burger", 10.50, 50)
        order = [{"item_id": "B1", "quantity": 2}]
        res = engine.process_order(order)
        self.assertEqual(res["status"], "ok")
        self.assertTrue("order_id" in res["value"])
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")
        
    def test_skills_engine(self):
        engine = OmniSkillsWebDevEngine()
        payload = {"code": "print('hello')", "context": "frontend"}
        res = engine.execute_skill("architecture_review", payload)
        self.assertEqual(res["status"], "ok")
        self.assertTrue("execution_id" in res["value"])
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")
        
    def test_erp_engine(self):
        engine = OmniErpSaasEngine()
        res = engine.provision_tenant("example.com", 1000)
        self.assertEqual(res["status"], "ok")
        tenant_id = res["value"]
        
        alloc = engine.allocate_resource(tenant_id, 200)
        self.assertEqual(alloc["status"], "ok")
        self.assertEqual(alloc["value"]["allocated"], 200)
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")
        
    def test_oxygen_engine(self):
        engine = OmniOxygenProjectEngine()
        res = engine.create_issue("Fix Bug", "Critical issue", "dev1")
        self.assertEqual(res["status"], "ok")
        issue_id = res["value"]
        
        trans = engine.transition_issue(issue_id, "DONE")
        self.assertEqual(trans["status"], "ok")
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_debithub_engine(self):
        engine = OmniDebithubBankingEngine()
        res1 = engine.open_account("USER-1", 5000.0)
        res2 = engine.open_account("USER-2", 100.0)
        
        self.assertEqual(res1["status"], "ok")
        acc1 = res1["value"]
        acc2 = res2["value"]
        
        tx = engine.process_transaction(acc1, acc2, 500.0)
        self.assertEqual(tx["status"], "ok")
        
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

