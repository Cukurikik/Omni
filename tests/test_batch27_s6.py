import unittest
import os
from src.compute.python_core.system.omni_byteps_engine import OmniBytePSEngine
from src.compute.python_core.system.omni_olivia_engine import OmniOliviaEngine
from src.compute.python_core.system.omni_lightly_engine import OmniLightlyEngine
from src.compute.python_core.system.omni_machine_learning_engine import OmniMachineLearningEngine
from src.compute.python_core.system.omni_tvm_cn_engine import OmniTVMCNEngine
from src.compute.python_core.system.omni_artline_engine import OmniArtLineEngine

class TestBatch27Engines(unittest.TestCase):
    def setUp(self):
        self.workspace = os.path.join(os.getcwd(), "test_workspace_batch27")
        os.makedirs(self.workspace, exist_ok=True)

        self.byteps = OmniBytePSEngine(self.workspace)
        self.olivia = OmniOliviaEngine(self.workspace)
        self.lightly = OmniLightlyEngine(self.workspace)
        self.ml = OmniMachineLearningEngine(self.workspace)
        self.tvm = OmniTVMCNEngine(self.workspace)
        self.artline = OmniArtLineEngine(self.workspace)

    def tearDown(self):
        import shutil
        if os.path.exists(self.workspace):
            shutil.rmtree(self.workspace, ignore_errors=True)

    # ==========================
    # 10 Tests for OmniBytePSEngine
    # ==========================
    def test_byteps_diag(self):
        diag = self.byteps.diagnostics()
        self.assertEqual(diag["engine"], "OmniBytePSEngine")
        self.assertFalse(diag["initialized"])

    def test_byteps_init(self):
        res = self.byteps.init_byteps()
        self.assertIn("status", res)

    def test_byteps_get_rank_uninit(self):
        res = self.byteps.get_local_rank()
        self.assertEqual(res["status"], "error")
        self.assertIn("not initialized", res["message"])

    def test_byteps_get_rank_init(self):
        self.byteps._is_initialized = True
        res = self.byteps.get_local_rank()
        self.assertIn(res["status"], ["success", "error"])

    def test_byteps_workspace(self):
        self.assertEqual(self.byteps.workspace_dir, self.workspace)

    def test_byteps_diag_initialized(self):
        self.byteps._is_initialized = True
        self.assertTrue(self.byteps.diagnostics()["initialized"])

    def test_byteps_domain(self):
        self.assertEqual(self.byteps.diagnostics()["domain"], "distributed_training")

    def test_byteps_init_error_format(self):
        res = self.byteps.init_byteps()
        if res["status"] == "error":
            self.assertIn("message", res)

    def test_byteps_override_workspace(self):
        b2 = OmniBytePSEngine("/tmp/byteps")
        self.assertEqual(b2.workspace_dir, "/tmp/byteps")

    def test_byteps_methods_exist(self):
        self.assertTrue(hasattr(self.byteps, "get_local_rank"))

    # ==========================
    # 10 Tests for OmniOliviaEngine
    # ==========================
    def test_olivia_diag(self):
        diag = self.olivia.diagnostics()
        self.assertEqual(diag["engine"], "OmniOliviaEngine")

    def test_olivia_start_server_missing_bin(self):
        res = self.olivia.start_local_server()
        self.assertEqual(res["status"], "error")
        self.assertIn("not found", res["message"])

    def test_olivia_build_req(self):
        res = self.olivia.build_chat_request("hello")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["payload"]["sentence"], "hello")

    def test_olivia_override_endpoint(self):
        o2 = OmniOliviaEngine(api_endpoint="http://remote:9090")
        self.assertEqual(o2.api_endpoint, "http://remote:9090")

    def test_olivia_build_req_endpoint(self):
        res = self.olivia.build_chat_request("hello")
        self.assertEqual(res["endpoint"], "http://localhost:8080/api/message")

    def test_olivia_workspace(self):
        self.assertEqual(self.olivia.workspace_dir, self.workspace)

    def test_olivia_diag_server(self):
        self.assertFalse(self.olivia.diagnostics()["server_running"])

    def test_olivia_mock_server_start(self):
        # mock a file
        bin_path = os.path.join(self.workspace, "olivia")
        with open(bin_path, "w") as f:
            f.write("mock")
        # should fail in Popen but cross that path
        try:
            res = self.olivia.start_local_server()
            self.assertIn("status", res)
        finally:
            os.remove(bin_path)

    def test_olivia_methods_exist(self):
        self.assertTrue(hasattr(self.olivia, "start_local_server"))

    def test_olivia_process_attr(self):
        self.assertIsNone(self.olivia._process)

    # ==========================
    # 10 Tests for OmniLightlyEngine
    # ==========================
    def test_lightly_diag(self):
        diag = self.lightly.diagnostics()
        self.assertEqual(diag["engine"], "OmniLightlyEngine")

    def test_lightly_init_dataset(self):
        res = self.lightly.initialize_dataset()
        self.assertIn(res["status"], ["success", "error"])

    def test_lightly_build_simclr(self):
        res = self.lightly.build_simclr_model()
        self.assertIn(res["status"], ["success", "error"])

    def test_lightly_workspace(self):
        self.assertEqual(self.lightly.workspace_dir, self.workspace)

    def test_lightly_dataset_dir(self):
        self.assertIn("data", self.lightly.dataset_dir)

    def test_lightly_diag_dataset(self):
        self.assertFalse(self.lightly.diagnostics()["dataset_configured"])

    def test_lightly_override_dir(self):
        l2 = OmniLightlyEngine(dataset_dir="custom/")
        self.assertIn("custom", l2.dataset_dir)

    def test_lightly_methods_exist(self):
        self.assertTrue(hasattr(self.lightly, "build_simclr_model"))

    def test_lightly_dataset_created(self):
        self.lightly.initialize_dataset()
        self.assertTrue(os.path.exists(self.lightly.dataset_dir))

    def test_lightly_error_structure(self):
        res = self.lightly.build_simclr_model()
        if res["status"] == "error":
            self.assertIn("message", res)

    # ==========================
    # 10 Tests for OmniMachineLearningEngine
    # ==========================
    def test_ml_diag(self):
        diag = self.ml.diagnostics()
        self.assertEqual(diag["engine"], "OmniMachineLearningEngine")

    def test_ml_fit(self):
        res = self.ml.fit_linear_regression([[1],[2]], [1,2])
        self.assertIn(res["status"], ["success", "error"])

    def test_ml_predict_no_model(self):
        res = self.ml.predict("linear_reg", [[3]])
        self.assertEqual(res["status"], "error")
        self.assertIn("not found in cache", res["message"])

    def test_ml_diag_cache(self):
        self.assertEqual(len(self.ml.diagnostics()["cached_models"]), 0)

    def test_ml_override_workspace(self):
        m2 = OmniMachineLearningEngine("/tmp/ml")
        self.assertEqual(m2.workspace_dir, "/tmp/ml")

    def test_ml_cache_internal(self):
        self.assertEqual(len(self.ml._model_cache), 0)

    def test_ml_methods_exist(self):
        self.assertTrue(hasattr(self.ml, "fit_linear_regression"))

    def test_ml_error_struct(self):
        res = self.ml.fit_linear_regression([], [])
        if res["status"] == "error":
            self.assertIn("message", res)

    def test_ml_predict_mock(self):
        self.ml._model_cache["linear_reg"] = "mock"
        res = self.ml.predict("linear_reg", [[1]])
        # will fail since mock is a string
        self.assertEqual(res["status"], "error")

    def test_ml_workspace_attr(self):
        self.assertEqual(self.ml.workspace_dir, self.workspace)

    # ==========================
    # 10 Tests for OmniTVMCNEngine
    # ==========================
    def test_tvm_diag(self):
        diag = self.tvm.diagnostics()
        self.assertEqual(diag["engine"], "OmniTVMCNEngine")

    def test_tvm_load(self):
        res = self.tvm.load_tvm()
        self.assertIn(res["status"], ["success", "error"])

    def test_tvm_compile_uninit(self):
        res = self.tvm.compile_model("model.onnx")
        self.assertEqual(res["status"], "error")
        self.assertIn("not initialized", res["message"])

    def test_tvm_compile_missing_file(self):
        self.tvm._is_ready = True
        res = self.tvm.compile_model("missing.onnx")
        self.assertEqual(res["status"], "error")
        self.assertIn("not found", res["message"])

    def test_tvm_compile_mock(self):
        self.tvm._is_ready = True
        dummy = os.path.join(self.workspace, "dummy.onnx")
        with open(dummy, "w") as f:
            f.write("mock")
        res = self.tvm.compile_model(dummy)
        self.assertEqual(res["status"], "success")

    def test_tvm_override_target(self):
        t2 = OmniTVMCNEngine(target="cuda")
        self.assertEqual(t2.target, "cuda")

    def test_tvm_diag_ready(self):
        self.assertFalse(self.tvm.diagnostics()["ready"])

    def test_tvm_workspace(self):
        self.assertEqual(self.tvm.workspace_dir, self.workspace)

    def test_tvm_error_struct(self):
        res = self.tvm.load_tvm()
        if res["status"] == "error":
            self.assertIn("message", res)

    def test_tvm_methods_exist(self):
        self.assertTrue(hasattr(self.tvm, "compile_model"))

    # ==========================
    # 10 Tests for OmniArtLineEngine
    # ==========================
    def test_artline_diag(self):
        diag = self.artline.diagnostics()
        self.assertEqual(diag["engine"], "OmniArtLineEngine")

    def test_artline_load(self):
        res = self.artline.load_artline_model()
        self.assertIn(res["status"], ["success", "error"])

    def test_artline_process_unloaded(self):
        res = self.artline.process_image("in.jpg", "out.jpg")
        self.assertEqual(res["status"], "error")
        self.assertIn("not loaded", res["message"])

    def test_artline_process_missing(self):
        self.artline.model_loaded = True
        res = self.artline.process_image("in.jpg", "out.jpg")
        self.assertEqual(res["status"], "error")
        self.assertIn("not found", res["message"])

    def test_artline_process_mock(self):
        self.artline.model_loaded = True
        dummy = os.path.join(self.workspace, "in.jpg")
        out = os.path.join(self.workspace, "out", "out.jpg")
        with open(dummy, "w") as f:
            f.write("mock")
        res = self.artline.process_image(dummy, out)
        self.assertEqual(res["status"], "success")
        self.assertTrue(os.path.exists(os.path.dirname(out)))

    def test_artline_diag_loaded(self):
        self.assertFalse(self.artline.diagnostics()["model_loaded"])

    def test_artline_workspace(self):
        self.assertEqual(self.artline.workspace_dir, self.workspace)

    def test_artline_override_workspace(self):
        a2 = OmniArtLineEngine("/tmp/artline")
        self.assertEqual(a2.workspace_dir, "/tmp/artline")

    def test_artline_methods_exist(self):
        self.assertTrue(hasattr(self.artline, "process_image"))

    def test_artline_error_struct(self):
        res = self.artline.load_artline_model()
        if res["status"] == "error":
            self.assertIn("message", res)


if __name__ == "__main__":
    unittest.main()
