import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestComputeLayer(unittest.TestCase):
    def test_sharegpt4video_sampler(self):
        from compute.sharegpt4video_sampler import VideoFrameSampler
        s = VideoFrameSampler()
        r = s.sample_uniform(1000, 10)
        self.assertTrue(r.is_ok)
        self.assertEqual(len(r.value), 10)

    def test_xrayglm_extractor_rejects_wrong_dim(self):
        from compute.xrayglm_extractor import XrayFeatureExtractor
        import torch
        ext = XrayFeatureExtractor()
        r = ext.extract(torch.randn(2, 3))  # 2D, should fail
        self.assertFalse(r.is_ok)

    def test_viscpm_processor(self):
        from compute.viscpm_processor import VisCPMProcessor
        import torch
        p = VisCPMProcessor()
        r = p.process_image_question(torch.randn(3, 224, 224), "What is this?", "en")
        self.assertTrue(r.is_ok)

    def test_caregpt_ner(self):
        from compute.caregpt_ner import MedicalNERExtractor
        ner = MedicalNERExtractor()
        r = ner.extract("Patient has fever and cough", ["SYMPTOM"])
        self.assertTrue(r.is_ok)

    def test_hackingbuddy_scanner(self):
        from compute.hackingbuddy_scanner import VulnScanner
        s = VulnScanner()
        r = s.scan_port_range(80, 90)
        self.assertTrue(r.is_ok)
        self.assertEqual(len(r.value), 11)

    def test_foundation_model_config(self):
        from compute.foundation_model_config import FoundationModelConfig
        cfg = FoundationModelConfig("test-model", 7.0, 4096)
        r = cfg.estimate_memory_gb()
        self.assertTrue(r.is_ok)
        self.assertAlmostEqual(r.value, 14.0)

if __name__ == "__main__":
    unittest.main(verbosity=2)
