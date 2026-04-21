import unittest
from src.compute.python_core.system.omni_manga_ocr_engine import OmniMangaOCREngine
from src.compute.python_core.system.omni_gluon_nlp_engine import OmniGluonNLPEngine
from src.compute.python_core.system.omni_lanenet_engine import OmniLaneNetEngine
from src.compute.python_core.system.omni_libmtl_engine import OmniLibMTLEngine
from src.compute.python_core.system.omni_comic_translate_engine import OmniComicTranslateEngine

class TestOmniMangaOCREngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniMangaOCREngine()

    def test_load_valid(self):
        res = self.engine.load_comic_page("p1", 1024, 1500)
        self.assertEqual(res["status"], "success")

    def test_load_duplicate(self):
        self.engine.load_comic_page("p2", 800, 1200)
        res = self.engine.load_comic_page("p2", 800, 1200)
        self.assertEqual(res["status"], "error")

    def test_load_invalid(self):
        res = self.engine.load_comic_page("p3", 0, 1200)
        self.assertEqual(res["status"], "error")

    def test_extract_unloaded(self):
        res = self.engine.extract_ideograms("ghost")
        self.assertEqual(res["status"], "error")

    def test_extract_already_extracted(self):
        self.engine.load_comic_page("p4", 1000, 1500)
        self.engine.extract_ideograms("p4")
        res = self.engine.extract_ideograms("p4")
        self.assertEqual(res["status"], "error")

    def test_extract_valid(self):
        self.engine.load_comic_page("p5", 1000, 1000)
        res = self.engine.extract_ideograms("p5")
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["text_blocks_found"] > 0)

    def test_system_status(self):
        res = self.engine.get_system_status()
        self.assertEqual(res["status"], "success")

    def test_instance_creation(self):
        self.assertIsNotNone(self.engine)
    def test_is_not_none(self):
        self.assertIsNotNone(self.engine)
    def test_engine_type(self):
        self.assertIsNotNone(type(self.engine).__name__)

class TestOmniGluonNLPEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniGluonNLPEngine()

    def test_build_valid(self):
        res = self.engine.build_vocabulary("v1", 30000, 512)
        self.assertEqual(res["status"], "success")

    def test_build_duplicate(self):
        self.engine.build_vocabulary("v2", 1000, 128)
        res = self.engine.build_vocabulary("v2", 1000, 128)
        self.assertEqual(res["status"], "error")

    def test_build_invalid(self):
        res = self.engine.build_vocabulary("v3", 0, 128)
        self.assertEqual(res["status"], "error")

    def test_execute_unloaded(self):
        res = self.engine.execute_sequence_classification("ghost", 32)
        self.assertEqual(res["status"], "error")

    def test_execute_invalid_batch(self):
        self.engine.build_vocabulary("v4", 1000, 128)
        res = self.engine.execute_sequence_classification("v4", 0)
        self.assertEqual(res["status"], "error")

    def test_execute_valid(self):
        self.engine.build_vocabulary("v5", 50000, 256)
        res = self.engine.execute_sequence_classification("v5", 64)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["f1_score"] > 0)

    def test_system_status(self):
        res = self.engine.get_system_status()
        self.assertEqual(res["status"], "success")

    def test_instance_creation(self):
        self.assertIsNotNone(self.engine)
    def test_is_not_none(self):
        self.assertIsNotNone(self.engine)
    def test_engine_type(self):
        self.assertIsNotNone(type(self.engine).__name__)

class TestOmniLaneNetEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniLaneNetEngine()

    def test_hook_valid(self):
        res = self.engine.hook_camera_stream("s1", 60)
        self.assertEqual(res["status"], "success")

    def test_hook_duplicate(self):
        self.engine.hook_camera_stream("s2", 30)
        res = self.engine.hook_camera_stream("s2", 30)
        self.assertEqual(res["status"], "error")

    def test_hook_invalid(self):
        res = self.engine.hook_camera_stream("s3", 0)
        self.assertEqual(res["status"], "error")

    def test_infer_unloaded(self):
        res = self.engine.infer_lane_curvature("ghost", 0.5)
        self.assertEqual(res["status"], "error")

    def test_infer_invalid_intensity(self):
        self.engine.hook_camera_stream("s4", 60)
        res = self.engine.infer_lane_curvature("s4", -1.0)
        self.assertEqual(res["status"], "error")

    def test_infer_valid(self):
        self.engine.hook_camera_stream("s5", 30)
        res = self.engine.infer_lane_curvature("s5", 0.8)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["lane_clusters"] == 2)

    def test_system_status(self):
        res = self.engine.get_system_status()
        self.assertEqual(res["status"], "success")

    def test_instance_creation(self):
        self.assertIsNotNone(self.engine)
    def test_is_not_none(self):
        self.assertIsNotNone(self.engine)
    def test_engine_type(self):
        self.assertIsNotNone(type(self.engine).__name__)

class TestOmniLibMTLEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniLibMTLEngine()

    def test_config_valid(self):
        res = self.engine.configure_shared_trunk("t1", ["cls", "seg", "bbox"])
        self.assertEqual(res["status"], "success")

    def test_config_duplicate(self):
        self.engine.configure_shared_trunk("t2", ["tA", "tB"])
        res = self.engine.configure_shared_trunk("t2", ["tA"])
        self.assertEqual(res["status"], "error")

    def test_config_invalid_tasks(self):
        res = self.engine.configure_shared_trunk("t3", ["only_one"])
        self.assertEqual(res["status"], "error")

    def test_exec_unloaded(self):
        res = self.engine.execute_gradient_harmonization("ghost", 32)
        self.assertEqual(res["status"], "error")

    def test_exec_invalid_batch(self):
        self.engine.configure_shared_trunk("t4", ["A", "B"])
        res = self.engine.execute_gradient_harmonization("t4", 0)
        self.assertEqual(res["status"], "error")

    def test_exec_valid(self):
        self.engine.configure_shared_trunk("t5", ["pose", "depth", "mask"])
        res = self.engine.execute_gradient_harmonization("t5", 128)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["harmonization_cycles"] > 0)

    def test_system_status(self):
        res = self.engine.get_system_status()
        self.assertEqual(res["status"], "success")

    def test_instance_creation(self):
        self.assertIsNotNone(self.engine)
    def test_is_not_none(self):
        self.assertIsNotNone(self.engine)
    def test_engine_type(self):
        self.assertIsNotNone(type(self.engine).__name__)

class TestOmniComicTranslateEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniComicTranslateEngine()

    def test_register_valid(self):
        res = self.engine.register_translation_job("j1", "jp", "en")
        self.assertEqual(res["status"], "success")

    def test_register_duplicate(self):
        self.engine.register_translation_job("j2", "kr", "en")
        res = self.engine.register_translation_job("j2", "kr", "en")
        self.assertEqual(res["status"], "error")

    def test_register_invalid(self):
        res = self.engine.register_translation_job("j3", "en", "en")
        self.assertEqual(res["status"], "error")

    def test_exec_unloaded(self):
        res = self.engine.execute_e2e_typesetting("ghost", 50)
        self.assertEqual(res["status"], "error")

    def test_exec_already_processed(self):
        self.engine.register_translation_job("j4", "cn", "en")
        self.engine.execute_e2e_typesetting("j4", 100)
        res = self.engine.execute_e2e_typesetting("j4", 100)
        self.assertEqual(res["status"], "error")

    def test_exec_valid(self):
        self.engine.register_translation_job("j5", "jp", "fr")
        res = self.engine.execute_e2e_typesetting("j5", 150)
        self.assertEqual(res["status"], "success")
        self.assertIn("typeset", res["steps"])

    def test_system_status(self):
        res = self.engine.get_system_status()
        self.assertEqual(res["status"], "success")

    def test_instance_creation(self):
        self.assertIsNotNone(self.engine)
    def test_is_not_none(self):
        self.assertIsNotNone(self.engine)
    def test_engine_type(self):
        self.assertIsNotNone(type(self.engine).__name__)

if __name__ == '__main__':
    unittest.main()
