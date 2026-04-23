"""
Integration Test Suite for OMNI Semester 10 Batch 41
Canonical migration from sem10_batch41_integration_tests.py
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import unittest
from src.compute.python_core.omni_alexa_emergency_system_engine import OmniAlexaEmergencySystemEngine
from src.compute.python_core.omni_autumn_mcp_engine import OmniAutumnMCPEngine
from src.compute.python_core.omni_brick_master_vr_engine import OmniBrickMasterVREngine
from src.compute.python_core.omni_dev_task_flow_engine import OmniDevTaskFlowEngine
from src.compute.python_core.omni_messaging_patterns_engine import OmniMessagingPatternsEngine

class TestBatch41Integration(unittest.TestCase):
    def test_alexa_emergency(self):
        engine = OmniAlexaEmergencySystemEngine()
        signals = [{"x": 3.0, "y": 4.0, "intensity": 10.0}]
        # distance = 5.0. 
        # weighted_x = 30.0, weighted_y = 40.0. total_intensity = 10.0. 
        # atten_factor = 1.0 + (10.0 / 5.0) = 3.0
        # center_x = 3.0, center_y = 4.0
        # conv_rad = 10.0 / 3.0 = 3.333...
        res = engine.calculate_signal_convergence(signals)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["center_x"], 3.0)
        self.assertEqual(res["value"]["center_y"], 4.0)
        self.assertAlmostEqual(res["value"]["convergence_radius"], 3.3333, places=3)
        self.assertEqual(res["value"]["total_intensity"], 10.0)

    def test_autumn_mcp(self):
        engine = OmniAutumnMCPEngine()
        conns = [{"bandwidth": 100.0, "packet_size": 10.0, "overhead": 0.0}]
        # throughput = 100 / 10 = 10.0. delay = 0.
        # eff = 10.0 / 1.0 = 10.0
        res = engine.compute_protocol_latency_topology(conns)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["total_throughput"], 10.0)
        self.assertEqual(res["value"]["structural_delay"], 0.0)
        self.assertEqual(res["value"]["concurrency_efficiency"], 10.0)

    def test_brick_master_vr(self):
        engine = OmniBrickMasterVREngine()
        voxels = [{"x": 0.0, "y": 0.0, "z": 0.0, "size": 2.0}]
        # min = [-1, -1, -1]. max = [1, 1, 1]. total volume = 8.
        # bounding volume = 2*2*2 = 8. density = 1.0.
        res = engine.compute_spatial_grid_collision(voxels)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["total_volume"], 8.0)
        self.assertEqual(res["value"]["bounding_volume"], 8.0)
        self.assertEqual(res["value"]["grid_density"], 1.0)

    def test_dev_task_flow(self):
        engine = OmniDevTaskFlowEngine()
        vectors = [{"action_weight": 2.0, "context_depth": 5.0}]
        # momentum = 4.0 + 5.0 = 9.0
        # complexity = 1.0 * (1 + 0.5) = 1.5
        # res_idx = 9.0 / 1.5 = 6.0
        res = engine.compute_action_matrix_bounds(vectors)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["vector_momentum"], 9.0)
        self.assertEqual(res["value"]["structural_complexity"], 1.5)
        self.assertEqual(res["value"]["resolution_index"], 6.0)

    def test_messaging_patterns(self):
        engine = OmniMessagingPatternsEngine()
        payloads = [{"size": 10.0, "processing_time": 2.0}]
        # total_mass = 10.0
        # queue_pressure = 20.0
        # latency_integral = 20.0 / 10.0 = 2.0
        # margins = 10.0 / (1.0 + 2.0) = 3.3333
        res = engine.model_queuing_latency_topology(payloads)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["value"]["total_payload_mass"], 10.0)
        self.assertEqual(res["value"]["queue_pressure_index"], 20.0)
        self.assertEqual(res["value"]["latency_integral"], 2.0)
        self.assertAlmostEqual(res["value"]["throughput_margins"], 3.3333, places=3)

