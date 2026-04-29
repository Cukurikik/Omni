import sys, os, unittest
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestComputeLayer(unittest.TestCase):
    def test_eagle_extractor(self):
        from compute.eagle_feature_extractor import EagleExtractor
        ext = EagleExtractor(100)
        r = ext.extract_features(np.random.randn(10, 10))
        self.assertTrue(r.is_ok)
        self.assertEqual(len(r.value), 100)

    def test_kgrag_retriever(self):
        from compute.kgrag_retriever import KGRAGRetriever
        r = KGRAGRetriever()
        r.add_triplet("Flu", "has_symptom", "Fever")
        res = r.retrieve_context("Flu")
        self.assertTrue(res.is_ok)
        self.assertEqual(res.value[0], "Flu has_symptom Fever")

    def test_factool_detector(self):
        from compute.factool_detector import FacToolDetector
        d = FacToolDetector()
        res = d.score_claim("The earth is round", ["Scientists confirm the earth is round"])
        self.assertTrue(res.is_ok)
        self.assertGreater(res.value, 0.5)

    def test_dataprep_cleaner(self):
        from compute.data_prep_cleaner import TextCleaner
        c = TextCleaner()
        r = c.clean_document("Check this out http://example.com  yes  ")
        self.assertTrue(r.is_ok)
        self.assertEqual(r.value, "Check this out yes")

    def test_omniquant_scaler(self):
        from compute.omniquant_scaler import LWCQuantizer
        q = LWCQuantizer()
        w = np.array([[-1.0, 0.0, 1.0], [2.0, 3.0, 4.0]])
        r = q.calculate_scales(w, 4)
        self.assertTrue(r.is_ok)
        self.assertEqual(r.value.shape, (2, 1))

    def test_llm_finetuner(self):
        from compute.llm_finetune_trainer import DPOFinetuner
        t = DPOFinetuner(0.1)
        r = t.compute_dpo_loss(-1.0, -2.0, -1.0, -2.0) # ratios are same, diff=0
        self.assertTrue(r.is_ok)
        self.assertAlmostEqual(r.value, 0.693147, places=4) # -log(0.5)

if __name__ == "__main__":
    unittest.main(verbosity=2)
