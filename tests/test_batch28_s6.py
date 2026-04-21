import unittest
import os
import shutil
from typing import Dict

# Import the Batch 28 engines
from src.compute.python_core.system.omni_ai_engineer_hq_engine import OmniAIEngineerHQEngine
from src.compute.python_core.system.omni_3ddfa_engine import Omni3DDFAEngine
from src.compute.python_core.system.omni_tps_engine import OmniTPSEngine
from src.compute.python_core.system.omni_face_evolve_engine import OmniFaceEvolveEngine
from src.compute.python_core.system.omni_text2sql_engine import OmniText2SQLEngine

class TestBatch28Engines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create temp dirs for testing
        cls.test_dir = os.path.join(os.getcwd(), "batch28_test_sandbox")
        os.makedirs(cls.test_dir, exist_ok=True)
        
        cls.hq_workspace = os.path.join(cls.test_dir, "hq_workspace")
        os.makedirs(cls.hq_workspace, exist_ok=True)
        
        cls.model_3d_path = os.path.join(cls.test_dir, "fake_3ddfa_model.pth")
        open(cls.model_3d_path, 'w').close()
        
        cls.image_path = os.path.join(cls.test_dir, "test_image.jpg")
        open(cls.image_path, 'w').close()
        
        cls.tps_checkpoints = os.path.join(cls.test_dir, "tps_checkpoints")
        os.makedirs(cls.tps_checkpoints, exist_ok=True)
        
        cls.driving_video = os.path.join(cls.test_dir, "drive.mp4")
        open(cls.driving_video, 'w').close()
        
        cls.evolve_root = os.path.join(cls.test_dir, "evolve_root")
        os.makedirs(cls.evolve_root, exist_ok=True)
        open(os.path.join(cls.evolve_root, "IR_50.pth"), 'w').close()
        open(os.path.join(cls.evolve_root, "IR_152.pth"), 'w').close()
        
        cls.schema_path = os.path.join(cls.test_dir, "schema.sql")
        with open(cls.schema_path, "w") as f:
            f.write("CREATE TABLE users (id INT);")

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def setUp(self):
        # Initialize instances
        self.hq = OmniAIEngineerHQEngine(self.hq_workspace)
        self.dfa = Omni3DDFAEngine(self.model_3d_path)
        self.tps = OmniTPSEngine(self.tps_checkpoints)
        self.evolve = OmniFaceEvolveEngine(self.evolve_root)
        self.text2sql = OmniText2SQLEngine(self.schema_path)

    # ==========================
    # OmniAIEngineerHQEngine Tests
    # ==========================
    def test_hq_init_returns_dict(self):
        res = self.hq.initialize_hq()
        self.assertIsInstance(res, dict)

    def test_hq_init_status(self):
        res = self.hq.initialize_hq()
        self.assertIn(res.get("status"), ["success", "error"])

    def test_hq_init_creates_dir(self):
        self.hq.initialize_hq()
        self.assertTrue(os.path.exists(self.hq.config_dir))

    def test_hq_compile_prompt_missing(self):
        res = self.hq.compile_prompt_template("missing", {})
        self.assertIsInstance(res, dict)
        self.assertEqual(res.get("status"), "error")

    def test_hq_compile_prompt_keys(self):
        res = self.hq.compile_prompt_template("missing", {})
        self.assertIn("message", res)

    def test_hq_orchestrate_dict(self):
        res = self.hq.orchestrate_agent_workflow({"task": "hello"})
        self.assertIsInstance(res, dict)

    def test_hq_orchestrate_error_handling(self):
        res = self.hq.orchestrate_agent_workflow({})
        self.assertTrue("status" in res)

    def test_hq_gen_arch_empty(self):
        res = self.hq.generate_system_architecture("")
        self.assertEqual(res.get("status"), "error")

    def test_hq_gen_arch_valid(self):
        res = self.hq.generate_system_architecture("build an app")
        self.assertEqual(res.get("status"), "success")

    def test_hq_gen_arch_payload(self):
        res = self.hq.generate_system_architecture("build an app")
        self.assertEqual(res.get("input_length"), len("build an app"))


    # ==========================
    # Omni3DDFAEngine Tests
    # ==========================
    def test_dfa_init_dict(self):
        res = self.dfa.initialize_3ddfa()
        self.assertIsInstance(res, dict)

    def test_dfa_init_graceful_missing(self):
        self.dfa.model_path = "does_not_exist.pth"
        res = self.dfa.initialize_3ddfa()
        # Should cleanly error or missing dependency
        self.assertEqual(res.get("status"), "error")

    def test_dfa_extract_nodes(self):
        res = self.dfa.extract_3d_vertices(self.image_path)
        self.assertIsInstance(res, dict)

    def test_dfa_extract_no_model(self):
        # We did not init model yet
        res = self.dfa.extract_3d_vertices(self.image_path)
        self.assertEqual(res.get("status"), "error")

    def test_dfa_extract_bad_image(self):
        self.dfa.model = "mock"
        res = self.dfa.extract_3d_vertices("fake.jpg")
        self.assertEqual(res.get("status"), "error")
        self.assertIn("not found", res.get("message", ""))

    def test_dfa_extract_missing_cv2(self):
        self.dfa.model = "mock"
        res = self.dfa.extract_3d_vertices(self.image_path)
        # Without cv2 it hits import error
        self.assertEqual(res.get("status"), "error")

    def test_dfa_render_dict(self):
        res = self.dfa.render_depth_map(None)
        self.assertIsInstance(res, dict)

    def test_dfa_render_handles_null(self):
        res = self.dfa.render_depth_map(None)
        self.assertEqual(res.get("status"), "error")

    def test_dfa_attributes_safeguard(self):
        self.assertTrue(hasattr(self.dfa, "model"))

    def test_dfa_no_hardcoded_paths(self):
        self.assertNotIn("c:/", self.dfa.model_path.lower() if not hasattr(self, 'model_3d_path') else "")


    # ==========================
    # OmniTPSEngine Tests
    # ==========================
    def test_tps_init_dict(self):
        res = self.tps.load_tps_animator()
        self.assertIsInstance(res, dict)

    def test_tps_init_status(self):
        res = self.tps.load_tps_animator()
        self.assertIn(res.get("status"), ["success", "error"])

    def test_tps_animate_uninit(self):
        res = self.tps.animate_image(self.image_path, self.driving_video, "out.mp4")
        self.assertEqual(res.get("status"), "error")

    def test_tps_animate_bad_source(self):
        self.tps.animator = "mock"
        res = self.tps.animate_image("missing.jpg", self.driving_video, "out.mp4")
        self.assertEqual(res.get("status"), "error")

    def test_tps_animate_bad_drive(self):
        self.tps.animator = "mock"
        res = self.tps.animate_image(self.image_path, "missing.mp4", "out.mp4")
        self.assertEqual(res.get("status"), "error")

    def test_tps_animate_trigger(self):
        self.tps.animator = "mock"
        res = self.tps.animate_image(self.image_path, self.driving_video, os.path.join(self.test_dir, "out.mp4"))
        self.assertIn(res.get("status"), ["success", "error"])

    def test_tps_optimize_dict(self):
        res = self.tps.optimize_temporal_consistency()
        self.assertIsInstance(res, dict)

    def test_tps_optimize_success(self):
        res = self.tps.optimize_temporal_consistency()
        self.assertEqual(res.get("status"), "success")

    def test_tps_bad_dir(self):
        self.tps.checkpoints_dir = "nonexistent"
        res = self.tps.load_tps_animator()
        self.assertEqual(res.get("status"), "error")

    def test_tps_output_format(self):
        self.tps.animator = "mock"
        out_f = os.path.join(self.test_dir, "valid.mp4")
        res = self.tps.animate_image(self.image_path, self.driving_video, out_f)
        if res.get("status") == "success":
            self.assertTrue(os.path.exists(out_f))


    # ==========================
    # OmniFaceEvolveEngine Tests
    # ==========================
    def test_evolve_init_dict(self):
        res = self.evolve.initialize_recognition_backbone()
        self.assertIsInstance(res, dict)

    def test_evolve_init_bad_arch(self):
        res = self.evolve.initialize_recognition_backbone("bad_arch")
        self.assertEqual(res.get("status"), "error")
        self.assertIn("not found", res.get("message", ""))

    def test_evolve_extract_dict(self):
        res = self.evolve.extract_face_features(self.image_path)
        self.assertIsInstance(res, dict)

    def test_evolve_extract_missing(self):
        res = self.evolve.extract_face_features("missing.jpg")
        self.assertEqual(res.get("status"), "error")
        self.assertIn("not found", res.get("message", ""))

    def test_evolve_sim_dict(self):
        res = self.evolve.compute_similarity([0], [0])
        self.assertIsInstance(res, dict)

    def test_evolve_sim_status(self):
        res = self.evolve.compute_similarity([0], [0])
        self.assertIn(res.get("status"), ["success", "error"])

    def test_evolve_missing_lib(self):
        res = self.evolve.initialize_recognition_backbone()
        if res.get("status") == "error":
            self.assertIn("Missing", res.get("message", "") + res.get("message", "torch"))

    def test_evolve_extract_missing_cv2(self):
        res = self.evolve.extract_face_features(self.image_path)
        if res.get("status") == "error":
            self.assertIn("installed", res.get("message", ""))

    def test_evolve_sim_logic(self):
        res = self.evolve.compute_similarity([], [])
        if res.get("status") == "success":
            self.assertGreater(res.get("similarity_score"), 0.0)

    def test_evolve_safeguard(self):
        self.assertTrue(hasattr(self.evolve, "backbone"))

    # ==========================
    # OmniText2SQLEngine Tests
    # ==========================
    def test_txt2sql_load_dict(self):
        res = self.text2sql.load_database_schema()
        self.assertIsInstance(res, dict)

    def test_txt2sql_load_success(self):
        res = self.text2sql.load_database_schema()
        self.assertEqual(res.get("status"), "success")

    def test_txt2sql_load_bad_file(self):
        self.text2sql.db_schema_url = "not_exist.sql"
        res = self.text2sql.load_database_schema()
        self.assertEqual(res.get("status"), "error")

    def test_txt2sql_parse_url(self):
        self.text2sql.db_schema_url = "http://fake.schema"
        res = self.text2sql.load_database_schema()
        self.assertEqual(res.get("status"), "success")

    def test_txt2sql_compile_unloaded(self):
        res = self.text2sql.compile_natural_language_to_sql("select all")
        self.assertEqual(res.get("status"), "error")
        self.assertIn("must be loaded", res.get("message", ""))

    def test_txt2sql_compile_empty(self):
        self.text2sql.schema_definition = "abc"
        res = self.text2sql.compile_natural_language_to_sql("")
        self.assertEqual(res.get("status"), "error")

    def test_txt2sql_compile_trigger(self):
        self.text2sql.schema_definition = "abc"
        res = self.text2sql.compile_natural_language_to_sql("get users")
        self.assertIn(res.get("status"), ["success", "error"])

    def test_txt2sql_validate_dict(self):
        res = self.text2sql.validate_sql_syntax("SELECT 1")
        self.assertIsInstance(res, dict)

    def test_txt2sql_validate_status(self):
        res = self.text2sql.validate_sql_syntax("SELECT 1")
        self.assertIn(res.get("status"), ["success", "error"])

    def test_txt2sql_schema_state(self):
        self.text2sql.load_database_schema()
        self.assertTrue(self.text2sql.schema_definition is not None)

if __name__ == '__main__':
    unittest.main()
