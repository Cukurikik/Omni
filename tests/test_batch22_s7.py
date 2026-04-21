# -*- coding: utf-8 -*-
"""
OMNI SEMESTER 7 — BATCH 22 INTEGRATION TESTS
Validates 3 Engines: OpenNMT, Spektral, TorchIO
"""
import unittest
from src.compute.python_core.system.omni_opennmt_engine import OmniOpenNMTEngine
from src.compute.python_core.system.omni_spektral_engine import OmniSpektralEngine
from src.compute.python_core.system.omni_torchio_engine import OmniTorchIOEngine

class TestOmniOpenNMTEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniOpenNMTEngine()

    def test_diagnostics_status(self):
        self.assertEqual(self.engine.diagnostics()["status"], "operational")

    def test_diagnostics_engine(self):
        self.assertEqual(self.engine.diagnostics()["engine"], "OmniOpenNMTEngine")

    def test_capabilities(self):
        caps = self.engine.diagnostics()["capabilities"]
        self.assertIsInstance(caps, list)
        self.assertGreater(len(caps), 0)

    def test_initialize_translation_pipeline(self):
        res = self.engine.initialize_translation_pipeline("transformer_v1")
        self.assertIsInstance(res, dict)
        self.assertIn("status", res)
        # Mock internal initialization state so translate works without relying on real imports
        self.engine.pipeline_initialized = True

    def test_translate_raw_sequence_uninitialized(self):
        res = self.engine.translate_raw_sequence("Hello", "en", "id")
        self.assertEqual(res["status"], "error")

    def test_translate_raw_sequence_initialized(self):
        self.engine.pipeline_initialized = True
        res = self.engine.translate_raw_sequence("Hello")
        self.assertEqual(res["status"], "success")

    def test_translate_raw_sequence_empty(self):
        self.engine.pipeline_initialized = True
        res = self.engine.translate_raw_sequence("")
        self.assertEqual(res["status"], "error")

    def test_fine_tune_nmt_model(self):
        res = self.engine.fine_tune_nmt_model("/tmp/data", 2)
        self.assertIsInstance(res, dict)
        self.assertIn("status", res)

    def test_instance_type(self):
        self.assertIsInstance(self.engine, OmniOpenNMTEngine)

    def test_callable(self):
        self.assertTrue(callable(self.engine.translate_raw_sequence))

    def test_diag_version(self):
        self.assertIn("version", self.engine.diagnostics())


class TestOmniSpektralEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniSpektralEngine()

    def test_diagnostics_status(self):
        self.assertEqual(self.engine.diagnostics()["status"], "operational")

    def test_diagnostics_engine(self):
        self.assertEqual(self.engine.diagnostics()["engine"], "OmniSpektralEngine")

    def test_capabilities(self):
        caps = self.engine.diagnostics()["capabilities"]
        self.assertGreater(len(caps), 0)

    def test_construct_graph_dataset(self):
        res = self.engine.construct_graph_dataset(10, 15)
        self.assertIsInstance(res, dict)
        self.assertIn("status", res)

    def test_build_gnn_topology(self):
        res = self.engine.build_gnn_topology(128)
        self.assertIsInstance(res, dict)
        self.assertIn("status", res)

    def test_predict_node_state_unbuilt(self):
        self.engine.topology_built = False
        res = self.engine.predict_node_state(1)
        self.assertEqual(res["status"], "error")

    def test_predict_node_state_built(self):
        self.engine.topology_built = True
        res = self.engine.predict_node_state(1)
        self.assertEqual(res["status"], "success")

    def test_instance_type(self):
        self.assertIsInstance(self.engine, OmniSpektralEngine)

    def test_callable(self):
        self.assertTrue(callable(self.engine.build_gnn_topology))

    def test_default_graph_type(self):
        self.assertEqual(self.engine.graph_type, "TUDataset")


class TestOmniTorchIOEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniTorchIOEngine()

    def test_diagnostics_status(self):
        self.assertEqual(self.engine.diagnostics()["status"], "operational")

    def test_diagnostics_engine(self):
        self.assertEqual(self.engine.diagnostics()["engine"], "OmniTorchIOEngine")

    def test_capabilities(self):
        caps = self.engine.diagnostics()["capabilities"]
        self.assertGreater(len(caps), 0)

    def test_load_medical_volume_invalid(self):
        res = self.engine.load_medical_volume(["not a string"])
        self.assertEqual(res["status"], "error")

    def test_load_medical_volume_valid(self):
        res = self.engine.load_medical_volume("brain_mri.nii.gz")
        self.assertIsInstance(res, dict)
        self.assertIn("status", res)

    def test_apply_spatial_transform_unloaded(self):
        self.engine.volume_loaded = False
        res = self.engine.apply_spatial_transform(90.0)
        self.assertEqual(res["status"], "error")

    def test_apply_spatial_transform_loaded(self):
        self.engine.volume_loaded = True
        res = self.engine.apply_spatial_transform(90.0)
        self.assertEqual(res["status"], "success")

    def test_generate_voxel_patches_unloaded(self):
        self.engine.volume_loaded = False
        res = self.engine.generate_voxel_patches(32)
        self.assertEqual(res["status"], "error")

    def test_generate_voxel_patches_loaded(self):
        self.engine.volume_loaded = True
        res = self.engine.generate_voxel_patches(32)
        self.assertEqual(res["status"], "success")

    def test_instance_type(self):
        self.assertIsInstance(self.engine, OmniTorchIOEngine)

    def test_callable(self):
        self.assertTrue(callable(self.engine.apply_spatial_transform))

    def test_diag_version(self):
        self.assertIn("version", self.engine.diagnostics())


if __name__ == "__main__":
    unittest.main()
