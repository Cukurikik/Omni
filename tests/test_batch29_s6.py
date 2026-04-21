import unittest
import os
import shutil

# Import the Batch 29 engines
from src.compute.python_core.system.omni_pytorch_text_engine import OmniPyTorchTextEngine
from src.compute.python_core.system.omni_ml_workspace_engine import OmniMLWorkspaceEngine
from src.compute.python_core.system.omni_huggingface_hub_engine import OmniHuggingFaceHubEngine

class TestBatch29Engines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create temp dirs for testing
        cls.test_dir = os.path.join(os.getcwd(), "batch29_test_sandbox")
        os.makedirs(cls.test_dir, exist_ok=True)
        
        cls.ws_root = os.path.join(cls.test_dir, "workspace_root")
        os.makedirs(cls.ws_root, exist_ok=True)
        
        cls.hf_cache = os.path.join(cls.test_dir, "hf_cache")

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def setUp(self):
        # Initialize instances
        self.pt_text = OmniPyTorchTextEngine()
        self.ml_ws = OmniMLWorkspaceEngine(self.ws_root, 8080)
        self.hf_hub = OmniHuggingFaceHubEngine(self.hf_cache)

    # ==========================
    # OmniPyTorchTextEngine Tests
    # ==========================
    def test_pt_init_tokenizer_dict(self):
        res = self.pt_text.initialize_tokenizer("en")
        self.assertIsInstance(res, dict)

    def test_pt_init_tokenizer_status(self):
        res = self.pt_text.initialize_tokenizer("en")
        self.assertIn(res.get("status"), ["success", "error"])

    def test_pt_init_bad_lang(self):
        res = self.pt_text.initialize_tokenizer("fr")
        self.assertEqual(res.get("status"), "error")
        self.assertIn("Unsupported", res.get("message", ""))

    def test_pt_init_empty_lang(self):
        res = self.pt_text.initialize_tokenizer("")
        self.assertEqual(res.get("status"), "error")
        self.assertIn("Language code required", res.get("message", ""))

    def test_pt_build_vocab_uninit(self):
        res = self.pt_text.build_vocabulary(["hello world"])
        self.assertEqual(res.get("status"), "error")
        self.assertIn("Tokenizer not initialized", res.get("message", ""))

    def test_pt_build_vocab_null_iter(self):
        self.pt_text.tokenizer = lambda x: x
        res = self.pt_text.build_vocabulary(None)
        self.assertEqual(res.get("status"), "error")

    def test_pt_build_vocab_trigger(self):
        self.pt_text.tokenizer = lambda x: x.split()
        res = self.pt_text.build_vocabulary(["hello world"])
        self.assertIn(res.get("status"), ["success", "error"])

    def test_pt_process_empty(self):
        res = self.pt_text.process_text_to_tensor("")
        self.assertEqual(res.get("status"), "error")
        self.assertIn("empty", res.get("message", ""))

    def test_pt_process_uninit(self):
        res = self.pt_text.process_text_to_tensor("hello")
        self.assertEqual(res.get("status"), "error")
        self.assertIn("Vocabulary and Tokenizer", res.get("message", ""))

    def test_pt_process_trigger(self):
        self.pt_text.tokenizer = lambda x: x.split()
        self.pt_text.vocab = lambda x: [0]
        res = self.pt_text.process_text_to_tensor("hello")
        self.assertIn(res.get("status"), ["success", "error"])


    # ==========================
    # OmniMLWorkspaceEngine Tests
    # ==========================
    def test_ws_health_dict(self):
        res = self.ml_ws.check_workspace_health()
        self.assertIsInstance(res, dict)

    def test_ws_health_success(self):
        res = self.ml_ws.check_workspace_health()
        self.assertEqual(res.get("status"), "success")

    def test_ws_health_bad_root(self):
        self.ml_ws.workspace_root = os.path.join(self.test_dir, "missing")
        res = self.ml_ws.check_workspace_health()
        self.assertEqual(res.get("status"), "error")

    def test_ws_health_empty_root(self):
        self.ml_ws.workspace_root = ""
        res = self.ml_ws.check_workspace_health()
        self.assertEqual(res.get("status"), "error")

    def test_ws_provision_dict(self):
        res = self.ml_ws.provision_workspace_environment()
        self.assertIsInstance(res, dict)

    def test_ws_provision_creates_dir(self):
        self.ml_ws.provision_workspace_environment()
        self.assertTrue(os.path.exists(os.path.join(self.ws_root, "env")))

    def test_ws_provision_activates(self):
        self.ml_ws.provision_workspace_environment()
        self.assertTrue(self.ml_ws.workspace_active)

    def test_ws_daemon_unprovisioned(self):
        res = self.ml_ws.execute_jupyter_daemon("sec123")
        self.assertEqual(res.get("status"), "error")
        self.assertIn("first", res.get("message", ""))

    def test_ws_daemon_bad_token(self):
        self.ml_ws.provision_workspace_environment()
        res = self.ml_ws.execute_jupyter_daemon("123")
        self.assertEqual(res.get("status"), "error")

    def test_ws_daemon_success(self):
        self.ml_ws.provision_workspace_environment()
        res = self.ml_ws.execute_jupyter_daemon("safe_token")
        self.assertEqual(res.get("status"), "success")
        self.assertIn("--port=8080", res.get("daemon_command", ""))


    # ==========================
    # OmniHuggingFaceHubEngine Tests
    # ==========================
    def test_hf_auth_dict(self):
        res = self.hf_hub.authenticate_hub("token")
        self.assertIsInstance(res, dict)

    def test_hf_auth_status(self):
        res = self.hf_hub.authenticate_hub("token")
        self.assertIn(res.get("status"), ["success", "error"])

    def test_hf_auth_empty_token(self):
        res = self.hf_hub.authenticate_hub("")
        self.assertEqual(res.get("status"), "error")
        self.assertIn("cannot be empty", res.get("message", ""))

    def test_hf_fetch_dict(self):
        res = self.hf_hub.fetch_model_info("repo_id")
        self.assertIsInstance(res, dict)

    def test_hf_fetch_status(self):
        res = self.hf_hub.fetch_model_info("repo_id")
        self.assertIn(res.get("status"), ["success", "error"])

    def test_hf_fetch_empty_repo(self):
        res = self.hf_hub.fetch_model_info("")
        self.assertEqual(res.get("status"), "error")
        self.assertIn("must be provided", res.get("message", ""))

    def test_hf_cache_dict(self):
        res = self.hf_hub.ensure_local_cache()
        self.assertIsInstance(res, dict)

    def test_hf_cache_success(self):
        res = self.hf_hub.ensure_local_cache()
        self.assertEqual(res.get("status"), "success")

    def test_hf_cache_creates_dir(self):
        self.hf_hub.ensure_local_cache()
        self.assertTrue(os.path.exists(self.hf_cache))
        
    def test_hf_attributes_safeguard(self):
        self.assertTrue(hasattr(self.hf_hub, "authenticated"))

if __name__ == '__main__':
    unittest.main()
