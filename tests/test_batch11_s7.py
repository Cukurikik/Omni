import unittest
from src.compute.python_core.system.omni_equinox_engine import OmniEquinoxEngine
from src.compute.python_core.system.omni_tensorrt_pro_engine import OmniTensorRTProEngine
from src.compute.python_core.system.omni_deepjazz_engine import OmniDeepJazzEngine
from src.compute.python_core.system.omni_thinc_engine import OmniThincEngine
from src.compute.python_core.system.omni_geoai_engine import OmniGeoAIEngine
from src.compute.python_core.system.omni_cv_in_action_engine import OmniCVInActionEngine

class TestOmniEquinoxEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniEquinoxEngine()

    def test_construct_valid_model(self):
        res = self.engine.construct_model("model_x", "MLP", seed=10)
        self.assertEqual(res["status"], "success")

    def test_construct_duplicate_model(self):
        self.engine.construct_model("model_x", "MLP")
        res = self.engine.construct_model("model_x", "CNN")
        self.assertEqual(res["status"], "error")

    def test_jit_compile_valid(self):
        self.engine.construct_model("model_y", "CNN")
        res = self.engine.jit_compile("model_y")
        self.assertEqual(res["status"], "success")

    def test_jit_compile_already_compiled(self):
        self.engine.construct_model("model_y", "CNN")
        self.engine.jit_compile("model_y")
        res = self.engine.jit_compile("model_y")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["message"], "Already compiled.")

    def test_jit_compile_invalid_model(self):
        res = self.engine.jit_compile("none_model")
        self.assertEqual(res["status"], "error")

    def test_evaluate_functional_not_compiled(self):
        self.engine.construct_model("model_eval", "MLP")
        res = self.engine.evaluate_functional("model_eval", [1.0, 2.0])
        self.assertEqual(res["status"], "error")

    def test_evaluate_functional_valid(self):
        self.engine.construct_model("model_eval2", "CNN")
        self.engine.jit_compile("model_eval2")
        res = self.engine.evaluate_functional("model_eval2", [10.0, 20.0])
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["output_tensor"], [9.5, 19.0])

    def test_system_status(self):
        res = self.engine.get_system_status()
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["engine"], "OmniEquinoxEngine")

class TestOmniTensorRTProEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniTensorRTProEngine()

    def test_load_engine_valid(self):
        res = self.engine.load_engine("yolov8_trt", "/models/yolov8.engine", "FP16", 4)
        self.assertEqual(res["status"], "success")

    def test_load_engine_invalid_precision(self):
        res = self.engine.load_engine("bad_trt", "/models/bad.engine", "FP64", 1)
        self.assertEqual(res["status"], "error")

    def test_execute_inference_unloaded(self):
        res = self.engine.execute_inference("ghost_model", [], 1)
        self.assertEqual(res["status"], "error")

    def test_execute_inference_exceeds_batch(self):
        self.engine.load_engine("ctx1", "model.engine", max_batch=2)
        res = self.engine.execute_inference("ctx1", [1, 2, 3], batch_size=4)
        self.assertEqual(res["status"], "error")

    def test_execute_inference_valid(self):
        self.engine.load_engine("ctx2", "model.engine", max_batch=4)
        res = self.engine.execute_inference("ctx2", [1, 2], batch_size=2)
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["detections"]), 2)

    def test_release_context_valid(self):
        self.engine.load_engine("ctx3", "x.engine")
        res = self.engine.release_context("ctx3")
        self.assertEqual(res["status"], "success")

    def test_release_context_invalid(self):
        res = self.engine.release_context("missing")
        self.assertEqual(res["status"], "error")

    def test_system_status(self):
        self.engine.load_engine("t1", "p1")
        res = self.engine.get_system_status()
        self.assertEqual(res["status"], "success")
        self.assertIn("t1", res["active_contexts"])

class TestOmniDeepJazzEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniDeepJazzEngine()

    def test_ingest_midi_valid(self):
        res = self.engine.ingest_midi_corpus("c1", ["C", "D", "E", "C", "D"])
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["vocab_size"], 3)

    def test_ingest_midi_empty(self):
        res = self.engine.ingest_midi_corpus("cempty", [])
        self.assertEqual(res["status"], "error")

    def test_generate_composition_missing_corpus(self):
        res = self.engine.generate_composition("none", 10)
        self.assertEqual(res["status"], "error")

    def test_generate_composition_invalid_length(self):
        self.engine.ingest_midi_corpus("c2", ["C", "D", "E"])
        res = self.engine.generate_composition("c2", 0)
        self.assertEqual(res["status"], "error")

    def test_generate_composition_valid(self):
        self.engine.ingest_midi_corpus("c3", ["C", "D", "E"])
        res = self.engine.generate_composition("c3", 5, 0.8)
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["composition"]), 5)
        for note in res["composition"]:
            self.assertIn(note, ["C", "D", "E"])

    def test_system_status(self):
        res = self.engine.get_system_status()
        self.assertEqual(res["status"], "success")

class TestOmniThincEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniThincEngine()

    def test_define_pipeline_valid(self):
        res = self.engine.define_pipeline("pipe1", ["Embed", "Maxout", "Softmax"])
        self.assertEqual(res["status"], "success")

    def test_define_pipeline_empty(self):
        res = self.engine.define_pipeline("pipe2", [])
        self.assertEqual(res["status"], "error")

    def test_define_duplicate(self):
        self.engine.define_pipeline("pipe1", ["Embed"])
        res = self.engine.define_pipeline("pipe1", ["Linear"])
        self.assertEqual(res["status"], "error")

    def test_compile_forward_pass_missing(self):
        res = self.engine.compile_forward_pass("ghost_pipe")
        self.assertEqual(res["status"], "error")

    def test_compile_forward_pass_valid(self):
        self.engine.define_pipeline("pipe3", ["Linear"])
        res = self.engine.compile_forward_pass("pipe3")
        self.assertEqual(res["status"], "success")

    def test_process_text_uncompiled(self):
        self.engine.define_pipeline("p_uncomp", ["Linear"])
        res = self.engine.process_text_batch("p_uncomp", ["hello"])
        self.assertEqual(res["status"], "error")

    def test_process_text_compiled(self):
        self.engine.define_pipeline("p_comp", ["Linear", "Softmax"])
        self.engine.compile_forward_pass("p_comp")
        res = self.engine.process_text_batch("p_comp", ["text1", "text2"])
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["batch_size"], 2)

    def test_system_status(self):
        res = self.engine.get_system_status()
        self.assertEqual(res["status"], "success")

class TestOmniGeoAIEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniGeoAIEngine()

    def test_load_satellite_raster_valid(self):
        res = self.engine.load_satellite_raster("reg1", [0.0, 0.0, 10.0, 10.0], 1.5)
        self.assertEqual(res["status"], "success")

    def test_load_satellite_raster_invalid_coords(self):
        res = self.engine.load_satellite_raster("reg2", [0.0, 10.0], 1.5)
        self.assertEqual(res["status"], "error")

    def test_extract_land_cover_missing(self):
        res = self.engine.extract_land_cover("reg_none")
        self.assertEqual(res["status"], "error")

    def test_extract_land_cover_valid(self):
        self.engine.load_satellite_raster("reg3", [1.0, 2.0, 3.0, 4.0], 0.5)
        res = self.engine.extract_land_cover("reg3", 0.90)
        self.assertEqual(res["status"], "success")
        # Features with confidence >= 0.90
        # Urban (0.95), Water (0.99) -> 2 features
        self.assertEqual(res["features_extracted"], 2)

    def test_system_status(self):
        res = self.engine.get_system_status()
        self.assertEqual(res["status"], "success")

class TestOmniCVInActionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniCVInActionEngine()

    def test_init_tracker_valid(self):
        res = self.engine.initialize_tracker("tr_1", "DeepSORT")
        self.assertEqual(res["status"], "success")

    def test_init_tracker_invalid_algo(self):
        res = self.engine.initialize_tracker("tr_2", "FakeSort")
        self.assertEqual(res["status"], "error")

    def test_init_tracker_duplicate(self):
        self.engine.initialize_tracker("tr_3")
        res = self.engine.initialize_tracker("tr_3")
        self.assertEqual(res["status"], "error")

    def test_process_frame_missing(self):
        res = self.engine.process_frame("missing", [255, 0, 0])
        self.assertEqual(res["status"], "error")

    def test_process_frame_empty(self):
        self.engine.initialize_tracker("tr_4")
        res = self.engine.process_frame("tr_4", [])
        self.assertEqual(res["status"], "error")

    def test_process_frame_valid(self):
        self.engine.initialize_tracker("tr_5")
        res = self.engine.process_frame("tr_5", [1, 2, 3, 4, 5])
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["objects_tracked"], 2)

    def test_destroy_tracker_valid(self):
        self.engine.initialize_tracker("tr_6")
        res = self.engine.destroy_tracker("tr_6")
        self.assertEqual(res["status"], "success")

    def test_destroy_tracker_invalid(self):
        res = self.engine.destroy_tracker("ghost")
        self.assertEqual(res["status"], "error")

    def test_system_status(self):
        res = self.engine.get_system_status()
        self.assertEqual(res["status"], "success")

if __name__ == '__main__':
    unittest.main()
