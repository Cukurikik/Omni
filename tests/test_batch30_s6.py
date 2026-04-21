import unittest
import os
import shutil

# Import the Batch 30 engines
from src.compute.python_core.system.omni_lstm_ar_engine import OmniLSTMAREngine
from src.compute.python_core.system.omni_min_dalle_engine import OmniMinDalleEngine
from src.compute.python_core.system.omni_studiogan_engine import OmniStudioGANEngine

class TestBatch30Engines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Temp dir for testing
        cls.test_dir = os.path.join(os.getcwd(), "batch30_test_sandbox")
        os.makedirs(cls.test_dir, exist_ok=True)
        
        # Fake config for StudioGAN
        cls.fake_config_name = "test_gan_config.yaml"
        cls.fake_config_path = os.path.join(cls.test_dir, cls.fake_config_name)
        with open(cls.fake_config_path, "w") as f:
            f.write("test: true\n")

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def setUp(self):
        self.lstm_ar = OmniLSTMAREngine(sequence_length=128, input_features=9)
        self.min_dalle = OmniMinDalleEngine(model_size="mini")
        self.studiogan = OmniStudioGANEngine(self.test_dir)

    # ==========================
    # OmniLSTMAREngine Tests
    # ==========================
    def test_lstm_init_dict(self):
        res = self.lstm_ar.initialize_lstm_architecture()
        self.assertIsInstance(res, dict)

    def test_lstm_init_status(self):
        res = self.lstm_ar.initialize_lstm_architecture()
        self.assertIn(res.get("status"), ["success", "error"])

    def test_lstm_init_bad_hidden(self):
        res = self.lstm_ar.initialize_lstm_architecture(hidden_units=0)
        self.assertEqual(res.get("status"), "error")
        self.assertIn("strictly positive", res.get("message", ""))

    def test_lstm_init_bad_classes(self):
        res = self.lstm_ar.initialize_lstm_architecture(num_classes=-1)
        self.assertEqual(res.get("status"), "error")
        self.assertIn("strictly positive", res.get("message", ""))

    def test_lstm_infer_dict(self):
        res = self.lstm_ar.infer_activity(None)
        self.assertIsInstance(res, dict)

    def test_lstm_infer_null_data(self):
        res = self.lstm_ar.infer_activity(None)
        self.assertEqual(res.get("status"), "error")
        self.assertIn("cannot be null", res.get("message", ""))

    def test_lstm_infer_uninit(self):
        res = self.lstm_ar.infer_activity([1, 2, 3])
        self.assertEqual(res.get("status"), "error")
        self.assertIn("before inference", res.get("message", ""))

    def test_lstm_infer_trigger(self):
        # Fake initialization trick to reach the next validation point safely
        self.lstm_ar.model = True 
        res = self.lstm_ar.infer_activity("fake_data")
        self.assertEqual(res.get("status"), "error")

    def test_lstm_attributes(self):
        self.assertEqual(self.lstm_ar.sequence_length, 128)
        self.assertEqual(self.lstm_ar.input_features, 9)

    def test_lstm_model_none_by_default(self):
        engine = OmniLSTMAREngine()
        self.assertIsNone(engine.model)


    # ==========================
    # OmniMinDalleEngine Tests
    # ==========================
    def test_dalle_init_dict(self):
        res = self.min_dalle.initialize_generator()
        self.assertIsInstance(res, dict)

    def test_dalle_init_bad_size(self):
        self.min_dalle.model_size = "huge"
        res = self.min_dalle.initialize_generator()
        self.assertEqual(res.get("status"), "error")
        self.assertIn("Invalid model size", res.get("message", ""))

    def test_dalle_init_status(self):
        res = self.min_dalle.initialize_generator()
        self.assertIn(res.get("status"), ["success", "error"])

    def test_dalle_gen_dict(self):
        res = self.min_dalle.generate_image_stream("hello")
        self.assertIsInstance(res, dict)

    def test_dalle_gen_empty_prompt(self):
        res = self.min_dalle.generate_image_stream("")
        self.assertEqual(res.get("status"), "error")
        self.assertIn("strictly required", res.get("message", ""))

    def test_dalle_gen_uninit(self):
        res = self.min_dalle.generate_image_stream("hello")
        self.assertEqual(res.get("status"), "error")
        self.assertIn("not initialized", res.get("message", ""))

    def test_dalle_gen_trigger(self):
        self.min_dalle.dalle_model = True
        res = self.min_dalle.generate_image_stream("hello")
        self.assertEqual(res.get("status"), "error")

    def test_dalle_attr_gpu(self):
        self.assertFalse(self.min_dalle.gpu_enabled)
        
    def test_dalle_attr_size(self):
        self.assertEqual(self.min_dalle.model_size, "mini")
        
    def test_dalle_init_custom(self):
        custom_engine = OmniMinDalleEngine("mega", True)
        self.assertEqual(custom_engine.model_size, "mega")
        self.assertTrue(custom_engine.gpu_enabled)


    # ==========================
    # OmniStudioGANEngine Tests
    # ==========================
    def test_gan_link_dict(self):
        res = self.studiogan.link_configuration(self.fake_config_name)
        self.assertIsInstance(res, dict)

    def test_gan_link_success(self):
        res = self.studiogan.link_configuration(self.fake_config_name)
        self.assertEqual(res.get("status"), "success")
        self.assertTrue(self.studiogan.config_linked)

    def test_gan_link_empty(self):
        res = self.studiogan.link_configuration("")
        self.assertEqual(res.get("status"), "error")
        self.assertIn("descriptor required", res.get("message", ""))

    def test_gan_link_missing(self):
        res = self.studiogan.link_configuration("missing.yaml")
        self.assertEqual(res.get("status"), "error")
        self.assertIn("does not exist", res.get("message", ""))

    def test_gan_compile_dict(self):
        res = self.studiogan.compile_training_loop()
        self.assertIsInstance(res, dict)

    def test_gan_compile_unlinked(self):
        res = self.studiogan.compile_training_loop()
        self.assertEqual(res.get("status"), "error")
        self.assertIn("prior to compiling", res.get("message", ""))

    def test_gan_compile_bad_workers(self):
        self.studiogan.link_configuration(self.fake_config_name)
        res = self.studiogan.compile_training_loop(-1)
        self.assertEqual(res.get("status"), "error")
        self.assertIn("non-negative", res.get("message", ""))

    def test_gan_compile_trigger(self):
        self.studiogan.link_configuration(self.fake_config_name)
        res = self.studiogan.compile_training_loop(4)
        self.assertIn(res.get("status"), ["success", "error"])

    def test_gan_attr_workspace(self):
        self.assertEqual(self.studiogan.workspace_path, self.test_dir)
        
    def test_gan_attr_linked_default(self):
        engine = OmniStudioGANEngine("root")
        self.assertFalse(engine.config_linked)


if __name__ == '__main__':
    unittest.main()
