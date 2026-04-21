# -*- coding: utf-8 -*-
"""
OMNI SEMESTER 7 — BATCH 5 INTEGRATION TESTS (ENRICHED)
Validates 5 Engines: FaceEvolve, Lightly, StudioGAN, Text2SQL, MultimodalOtter
50+ tests with functional coverage.
"""
import unittest
import tempfile
from src.compute.python_core.system.omni_face_evolve_engine import OmniFaceEvolveEngine
from src.compute.python_core.system.omni_lightly_engine import OmniLightlyEngine
from src.compute.python_core.system.omni_studiogan_engine import OmniStudioGANEngine
from src.compute.python_core.system.omni_text2sql_engine import OmniText2SQLEngine
from src.compute.python_core.system.omni_multimodal_otter_engine import OmniMultimodalOtterEngine


class TestOmniFaceEvolveEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniFaceEvolveEngine(model_root=tempfile.gettempdir())

    def test_diagnostics_status(self):
        self.assertEqual(self.engine.diagnostics()["status"], "operational")

    def test_engine_name(self):
        self.assertEqual(self.engine.diagnostics()["engine"], "OmniFaceEvolveEngine")

    def test_version(self):
        self.assertEqual(self.engine.diagnostics()["version"], "1.0.0")

    def test_capabilities(self):
        caps = self.engine.diagnostics()["capabilities"]
        self.assertIsInstance(caps, list)
        self.assertIn("extract_face_embedding", caps)

    def test_full_structure(self):
        for k in ["status", "engine", "version", "capabilities"]:
            self.assertIn(k, self.engine.diagnostics())

    def test_consistency(self):
        self.assertEqual(self.engine.diagnostics(), self.engine.diagnostics())

    def test_extract_face_features_returns_dict(self):
        res = self.engine.extract_face_features(aligned_image_path="/tmp/test.jpg")
        self.assertIsInstance(res, dict)
        self.assertIn("status", res)

    def test_compute_similarity_returns_dict(self):
        res = self.engine.compute_similarity(embedding1=[0.1]*128, embedding2=[0.2]*128)
        self.assertIsInstance(res, dict)
        self.assertIn("status", res)

    def test_instance_type(self):
        self.assertIsInstance(self.engine, OmniFaceEvolveEngine)

    def test_caps_all_strings(self):
        for cap in self.engine.diagnostics()["capabilities"]:
            self.assertIsInstance(cap, str)


class TestOmniLightlyEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniLightlyEngine()

    def test_diagnostics_status(self):
        self.assertEqual(self.engine.diagnostics()["status"], "operational")

    def test_engine_name(self):
        self.assertEqual(self.engine.diagnostics()["engine"], "OmniLightlyEngine")

    def test_version(self):
        self.assertEqual(self.engine.diagnostics()["version"], "1.0.0")

    def test_capabilities(self):
        caps = self.engine.diagnostics()["capabilities"]
        self.assertIsInstance(caps, list)
        self.assertIn("initialize_dataset", caps)
        self.assertIn("build_simclr_model", caps)

    def test_dataset_configured_false(self):
        self.assertFalse(self.engine.diagnostics()["dataset_configured"])

    def test_dataset_dir_present(self):
        self.assertIn("dataset_dir", self.engine.diagnostics())

    def test_full_structure(self):
        for k in ["status", "engine", "version", "capabilities"]:
            self.assertIn(k, self.engine.diagnostics())

    def test_consistency(self):
        self.assertEqual(self.engine.diagnostics(), self.engine.diagnostics())

    def test_instance_type(self):
        self.assertIsInstance(self.engine, OmniLightlyEngine)

    def test_is_dict(self):
        self.assertIsInstance(self.engine.diagnostics(), dict)


class TestOmniStudioGANEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniStudioGANEngine(workspace_path=tempfile.gettempdir())

    def test_diagnostics_status(self):
        self.assertEqual(self.engine.diagnostics()["status"], "operational")

    def test_engine_name(self):
        self.assertEqual(self.engine.diagnostics()["engine"], "OmniStudioGANEngine")

    def test_version(self):
        self.assertEqual(self.engine.diagnostics()["version"], "1.0.0")

    def test_capabilities(self):
        caps = self.engine.diagnostics()["capabilities"]
        self.assertIsInstance(caps, list)
        self.assertIn("link_configuration", caps)

    def test_full_structure(self):
        for k in ["status", "engine", "version", "capabilities"]:
            self.assertIn(k, self.engine.diagnostics())

    def test_link_configuration_returns_dict(self):
        res = self.engine.link_configuration(config_file="/tmp/config.yaml")
        self.assertIsInstance(res, dict)
        self.assertIn("status", res)

    def test_compile_training_loop_returns_dict(self):
        res = self.engine.compile_training_loop()
        self.assertIsInstance(res, dict)
        self.assertIn("status", res)

    def test_consistency(self):
        self.assertEqual(self.engine.diagnostics(), self.engine.diagnostics())

    def test_instance_type(self):
        self.assertIsInstance(self.engine, OmniStudioGANEngine)

    def test_caps_non_empty(self):
        self.assertGreater(len(self.engine.diagnostics()["capabilities"]), 0)


class TestOmniText2SQLEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniText2SQLEngine(db_schema_url="sqlite:///test.db")

    def test_diagnostics_status(self):
        self.assertEqual(self.engine.diagnostics()["status"], "operational")

    def test_engine_name(self):
        self.assertEqual(self.engine.diagnostics()["engine"], "OmniText2SQLEngine")

    def test_version(self):
        self.assertEqual(self.engine.diagnostics()["version"], "1.0.0")

    def test_capabilities(self):
        caps = self.engine.diagnostics()["capabilities"]
        self.assertIsInstance(caps, list)
        self.assertIn("compile_nl_to_sql", caps)

    def test_full_structure(self):
        for k in ["status", "engine", "version", "capabilities"]:
            self.assertIn(k, self.engine.diagnostics())

    def test_load_schema_returns_dict(self):
        res = self.engine.load_database_schema()
        self.assertIsInstance(res, dict)
        self.assertIn("status", res)

    def test_validate_sql_returns_dict(self):
        res = self.engine.validate_sql_syntax(generated_sql="SELECT * FROM users")
        self.assertIsInstance(res, dict)
        self.assertIn("status", res)

    def test_consistency(self):
        self.assertEqual(self.engine.diagnostics(), self.engine.diagnostics())

    def test_instance_type(self):
        self.assertIsInstance(self.engine, OmniText2SQLEngine)

    def test_caps_unique(self):
        c = self.engine.diagnostics()["capabilities"]
        self.assertEqual(len(c), len(set(c)))


class TestOmniMultimodalOtterEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniMultimodalOtterEngine()

    def test_diagnostics_status(self):
        self.assertEqual(self.engine.diagnostics()["status"], "operational")

    def test_engine_name(self):
        self.assertEqual(self.engine.diagnostics()["engine"], "OmniMultimodalOtterEngine")

    def test_version(self):
        self.assertEqual(self.engine.diagnostics()["version"], "1.0.0")

    def test_capabilities(self):
        caps = self.engine.diagnostics()["capabilities"]
        self.assertIsInstance(caps, list)
        self.assertGreater(len(caps), 3)

    def test_full_structure(self):
        for k in ["status", "engine", "version", "capabilities"]:
            self.assertIn(k, self.engine.diagnostics())

    def test_list_models_returns_dict(self):
        res = self.engine.list_models()
        self.assertIsInstance(res, dict)
        self.assertIn("status", res)

    def test_dataset_format_info_returns_dict(self):
        res = self.engine.dataset_format_info()
        self.assertIsInstance(res, dict)
        self.assertIn("status", res)

    def test_consistency(self):
        self.assertEqual(self.engine.diagnostics(), self.engine.diagnostics())

    def test_instance_type(self):
        self.assertIsInstance(self.engine, OmniMultimodalOtterEngine)

    def test_caps_all_strings(self):
        for cap in self.engine.diagnostics()["capabilities"]:
            self.assertIsInstance(cap, str)


if __name__ == "__main__":
    unittest.main()
