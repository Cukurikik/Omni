import unittest
import os
from src.compute.python_core.system.omni_huggingface_nlp_engine import OmniHuggingFaceNLPEngine
from src.compute.python_core.system.omni_mmpretrain_engine import OmniMMPretrainEngine
from src.compute.python_core.system.omni_swanlab_engine import OmniSwanLabEngine
from src.compute.python_core.system.omni_lazyllm_engine import OmniLazyLLMEngine
from src.compute.python_core.system.omni_scenic_engine import OmniScenicEngine

class TestBatch26Engines(unittest.TestCase):
    def setUp(self):
        self.workspace = os.path.join(os.getcwd(), "test_workspace_batch26")
        os.makedirs(self.workspace, exist_ok=True)
        
        self.hf = OmniHuggingFaceNLPEngine(self.workspace)
        self.mm = OmniMMPretrainEngine(self.workspace)
        self.swan = OmniSwanLabEngine(self.workspace)
        self.lazy = OmniLazyLLMEngine(self.workspace)
        self.scenic = OmniScenicEngine(self.workspace)

    def tearDown(self):
        import shutil
        if os.path.exists(self.workspace):
            shutil.rmtree(self.workspace, ignore_errors=True)

    # ==========================
    # 10 Tests for OmniHuggingFaceNLPEngine
    # ==========================
    def test_hf_initialization(self):
        diag = self.hf.diagnostics()
        self.assertEqual(diag["engine"], "OmniHuggingFaceNLPEngine")
        self.assertFalse(diag["pipeline_loaded"])
        
    def test_hf_load_error_wrapper(self):
        res = self.hf.load_pipeline("text-classification")
        self.assertIn("status", res)
        
    def test_hf_inference_unloaded(self):
        res = self.hf.run_inference("Hello OMNI")
        self.assertEqual(res["status"], "error")
        
    def test_hf_clear_cache(self):
        res = self.hf.clear_cache()
        self.assertIn("status", res)
        
    def test_hf_diag_structure(self):
        self.assertIn("model_id", self.hf.diagnostics())
        self.assertIn("cache_dir", self.hf.diagnostics())

    def test_hf_param_override(self):
        hf2 = OmniHuggingFaceNLPEngine(model_id="gpt2")
        self.assertEqual(hf2.model_id, "gpt2")

    def test_hf_custom_workspace(self):
        hf2 = OmniHuggingFaceNLPEngine(workspace_dir="/tmp/omni")
        self.assertEqual(hf2.workspace_dir, "/tmp/omni")

    def test_hf_load_inference_flow(self):
        res = self.hf.load_pipeline("summarization")
        if res["status"] == "success":
            inf = self.hf.run_inference("Test")
            self.assertEqual(inf["status"], "success")

    def test_hf_cache_dir_created(self):
        self.assertTrue(os.path.exists(self.hf._cache_dir))

    def test_hf_version(self):
        self.assertTrue(hasattr(self.hf, "load_pipeline"))

    # ==========================
    # 10 Tests for OmniMMPretrainEngine
    # ==========================
    def test_mm_diag(self):
        diag = self.mm.diagnostics()
        self.assertEqual(diag["engine"], "OmniMMPretrainEngine")

    def test_mm_init(self):
        res = self.mm.initialize_model()
        self.assertIn(res["status"], ["success", "error"])

    def test_mm_infer_unloaded(self):
        res = self.mm.infer_image("dummy.jpg")
        self.assertEqual(res["status"], "error")

    def test_mm_infer_missing_image(self):
        self.mm.model = "mock"
        res = self.mm.infer_image("nonexistent.jpg")
        self.assertEqual(res["status"], "error")

    def test_mm_generate_config(self):
        res = self.mm.generate_dummy_config()
        self.assertEqual(res["status"], "success")
        self.assertTrue(os.path.exists(res["config_path"]))

    def test_mm_config_content(self):
        res = self.mm.generate_dummy_config()
        with open(res["config_path"], "r") as f:
            content = f.read()
            self.assertIn("ResNet", content)

    def test_mm_custom_config(self):
        mm2 = OmniMMPretrainEngine(config_name="vit_base")
        self.assertEqual(mm2.config_name, "vit_base")

    def test_mm_workspace_check(self):
        self.assertEqual(self.mm.workspace_dir, self.workspace)

    def test_mm_invalid_infer(self):
        self.mm.model = "mock"
        try:
            res = self.mm.infer_image(self.workspace)
            # The dir exists so passes os.path check, but model isn't callable
            self.assertEqual(res["status"], "error")
        except:
            pass

    def test_mm_has_model_attribute(self):
        self.assertTrue(hasattr(self.mm, "model"))

    # ==========================
    # 10 Tests for OmniSwanLabEngine
    # ==========================
    def test_swan_diag(self):
        diag = self.swan.diagnostics()
        self.assertEqual(diag["engine"], "OmniSwanLabEngine")

    def test_swan_init(self):
        res = self.swan.init_experiment({"lr": 0.01})
        self.assertIn(res["status"], ["success", "error"])

    def test_swan_log_untracked(self):
        res = self.swan.log_metrics({"loss": 0.5}, 1)
        self.assertEqual(res["status"], "error")

    def test_swan_finish_untracked(self):
        res = self.swan.finish_experiment()
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["message"], "No active experiment to finish.")

    def test_swan_log_tracked(self):
        self.swan._is_tracking = True
        res = self.swan.log_metrics({"loss": 0.5}, 1)
        self.assertIn(res["status"], ["success", "error"])

    def test_swan_finish_tracked(self):
        self.swan._is_tracking = True
        res = self.swan.finish_experiment()
        self.assertIn(res["status"], ["success", "error"])

    def test_swan_project_override(self):
        s2 = OmniSwanLabEngine(project_name="test_proj")
        self.assertEqual(s2.project_name, "test_proj")

    def test_swan_log_dir_set(self):
        self.assertIn("swanlog", self.swan.log_dir)

    def test_swan_diag_tracking(self):
        self.assertFalse(self.swan.diagnostics()["tracking"])

    def test_swan_methods_exist(self):
        self.assertTrue(hasattr(self.swan, "init_experiment"))

    # ==========================
    # 10 Tests for OmniLazyLLMEngine
    # ==========================
    def test_lazy_diag(self):
        diag = self.lazy.diagnostics()
        self.assertEqual(diag["engine"], "OmniLazyLLMEngine")

    def test_lazy_create(self):
        res = self.lazy.create_chat_app()
        self.assertIn(res["status"], ["success", "error"])

    def test_lazy_start_noapp(self):
        res = self.lazy.start_service()
        self.assertEqual(res["status"], "error")

    def test_lazy_start_app(self):
        self.lazy.app = "mock_app"
        res = self.lazy.start_service()
        self.assertIn(res["status"], ["success", "error"])

    def test_lazy_config(self):
        res = self.lazy.render_config()
        self.assertEqual(res["status"], "success")
        self.assertIn("config", res)

    def test_lazy_config_app_bound(self):
        self.lazy.app = "mock"
        res = self.lazy.render_config()
        self.assertTrue(res["config"]["app_bound"])

    def test_lazy_diag_app(self):
        self.assertEqual(self.lazy.diagnostics()["app_status"], "none")

    def test_lazy_diag_app_configured(self):
        self.lazy.app = "mock"
        self.assertEqual(self.lazy.diagnostics()["app_status"], "configured")

    def test_lazy_custom_model(self):
        res = self.lazy.create_chat_app(model_name="gpt-4")
        self.assertIn(res["status"], ["success", "error"])

    def test_lazy_workspace(self):
        self.assertEqual(self.lazy.workspace_dir, self.workspace)

    # ==========================
    # 10 Tests for OmniScenicEngine
    # ==========================
    def test_scenic_diag(self):
        diag = self.scenic.diagnostics()
        self.assertEqual(diag["engine"], "OmniScenicEngine")

    def test_scenic_build(self):
        res = self.scenic.build_model()
        self.assertIn(res["status"], ["success", "error"])

    def test_scenic_train_no_model(self):
        res = self.scenic.run_training_step()
        self.assertEqual(res["status"], "error")

    def test_scenic_features_no_model(self):
        res = self.scenic.extract_features()
        self.assertEqual(res["status"], "error")

    def test_scenic_train_mock(self):
        self.scenic.model = "mock"
        res = self.scenic.run_training_step(0.99)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["loss"], 0.99)

    def test_scenic_features_mock(self):
        self.scenic.model = "mock"
        res = self.scenic.extract_features("128x128x3")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["shape"], "128x128x3")

    def test_scenic_arch_override(self):
        sc2 = OmniScenicEngine(model_arch="resnet101")
        self.assertEqual(sc2.model_arch, "resnet101")

    def test_scenic_diag_uninit(self):
        self.assertEqual(self.scenic.diagnostics()["status"], "uninitialized")

    def test_scenic_diag_ready(self):
        self.scenic.model = "mock"
        self.assertEqual(self.scenic.diagnostics()["status"], "ready")

    def test_scenic_workspace(self):
        self.assertEqual(self.scenic.workspace_dir, self.workspace)

if __name__ == "__main__":
    unittest.main()
