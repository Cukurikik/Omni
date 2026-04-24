import unittest
from src.compute.python_core.omni_showo_engine import OmniShowoEngine
from src.compute.python_core.omni_advanced_literate_machinery_engine import OmniAdvancedLiterateMachineryEngine
from src.compute.python_core.omni_qwen_vl_series_finetune_engine import OmniQwenVlSeriesFinetuneEngine
from src.compute.python_core.omni_alan_sdk_android_engine import OmniAlanSdkAndroidEngine
from src.compute.python_core.omni_alan_sdk_flutter_engine import OmniAlanSdkFlutterEngine
from src.compute.python_core.omni_detikzify_engine import OmniDetikzifyEngine
from src.compute.python_core.omni_data_designer_engine import OmniDataDesignerEngine
from src.compute.python_core.omni_alan_sdk_ionic_engine import OmniAlanSdkIonicEngine
from src.compute.python_core.omni_meta_transformer_engine import OmniMetaTransformerEngine
import asyncio
from src.compute.python_core.omni_moss_tts_engine import OmniMossTTSEngine

class TestSemester12Batch6(unittest.TestCase):
    def test_showo_engine(self):
        engine = OmniShowoEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniShowoEngine")
        
        res = engine.process_multimodal_request("point_cloud")
        self.assertTrue(res.is_ok())
        
    def test_advanced_literate_machinery_engine(self):
        engine = OmniAdvancedLiterateMachineryEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniAdvancedLiterateMachineryEngine")
        
        res = engine.extract_document_text(b"pdf_bytes")
        self.assertTrue(res.is_ok())

    def test_qwen_vl_series_finetune_engine(self):
        engine = OmniQwenVlSeriesFinetuneEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniQwenVlSeriesFinetuneEngine")
        
        res = engine.execute_finetuning_job("dataset.jsonl", "output_dir")
        self.assertTrue(res.is_ok())

    def test_alan_sdk_android_engine(self):
        engine = OmniAlanSdkAndroidEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniAlanSdkAndroidEngine")
        
        res = engine.bundle_voice_model({"model": "test"})
        self.assertTrue(res.is_ok())

    def test_alan_sdk_flutter_engine(self):
        engine = OmniAlanSdkFlutterEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniAlanSdkFlutterEngine")
        
        res = engine.generate_method_channels(["HomeScreen"])
        self.assertTrue(res.is_ok())

    def test_detikzify_engine(self):
        engine = OmniDetikzifyEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniDetikzifyEngine")
        
        res = engine.synthesize_tikz("image_tensor")
        self.assertTrue(res.is_ok())

    def test_data_designer_engine(self):
        engine = OmniDataDesignerEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniDataDesignerEngine")
        
        res = engine.generate_synthetic_samples([{"test": 1}], 5)
        self.assertTrue(res.is_ok())

    def test_alan_sdk_ionic_engine(self):
        engine = OmniAlanSdkIonicEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniAlanSdkIonicEngine")
        
        res = engine.link_voice_components(["/home"])
        self.assertTrue(res.is_ok())

    def test_meta_transformer_engine(self):
        engine = OmniMetaTransformerEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine"], "OmniMetaTransformerEngine")
        
        res = engine.forward_unified({"image": "tensor"})
        self.assertTrue(res.is_ok())

    def test_moss_tts_engine(self):
        engine = OmniMossTTSEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["engine_id"], "omni-moss-t-t-s")
        
        res = asyncio.run(engine.synthesize_speech("Hello"))
        self.assertTrue(res.is_ok)

if __name__ == '__main__':
    unittest.main()
