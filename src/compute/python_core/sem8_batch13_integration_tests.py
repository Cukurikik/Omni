"""
Semester 8 Batch 13 — Integration Tests
=======================================
Validates all 5 Batch 13 engines:
  1. OmniAICollegeJobsEngine
  2. OmniAwesomeMLOpsEngine
  3. OmniEagleEyeEngine
  4. OmniLightFMEngine
  5. OmniMarqoEngine

All operations are zero-mock using pure python/NumPy.
"""

import unittest
import numpy as np

from omni_ai_college_jobs_engine import OmniAICollegeJobsEngine
from omni_awesome_mlops_engine import OmniAwesomeMLOpsEngine, MLOpsTool, MLOpsPipelineDef
from omni_eagleeye_engine import OmniEagleEyeEngine, SocialProfile, FaceEmbedding
from omni_lightfm_engine import OmniLightFMEngine
from omni_marqo_engine import OmniMarqoEngine

# ---------------------------------------------------------------------------
# Monadic Helpers
# ---------------------------------------------------------------------------
def is_ok(result) -> bool:
    return hasattr(result, "value") and not hasattr(result, "error")

def is_err(result) -> bool:
    return hasattr(result, "error") and not hasattr(result, "value")

def unwrap(result):
    return result.value


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------

class TestAICollegeJobsEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniAICollegeJobsEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_resume_parser(self):
        engine = OmniAICollegeJobsEngine()
        parser = engine.get_parser()
        
        cv_text = "I am a Python developer with experience in PyTorch and MLOps. Also Docker."
        res = parser.parse(cv_text)
        self.assertTrue(is_ok(res))
        skills = unwrap(res)
        
        self.assertIn("python", skills)
        self.assertIn("pytorch", skills)
        self.assertIn("mlops", skills)
        self.assertIn("docker", skills)
        self.assertNotIn("c++", skills)

    def test_evaluate_candidate(self):
        engine = OmniAICollegeJobsEngine()
        cv_text = "Worked deeply with Python, Pandas, SQL, and Scikit-learn to build models."
        res = engine.evaluate_candidate("cand_1", cv_text)
        
        self.assertTrue(is_ok(res))
        profile = unwrap(res)
        
        self.assertEqual(profile.id, "cand_1")
        # Data Scientist should have high score due to pandas, sql, scikit-learn, python
        ds_score = profile.role_scores.get("Data Scientist", 0)
        ml_score = profile.role_scores.get("ML Engineer", 0)
        self.assertGreater(ds_score, ml_score)


class TestAwesomeMLOpsEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniAwesomeMLOpsEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_seed_and_search(self):
        engine = OmniAwesomeMLOpsEngine()
        engine.seed_default_tools()
        
        res = engine.taxonomy.search_by_phase("monitoring")
        self.assertTrue(is_ok(res))
        tools = unwrap(res)
        self.assertGreater(len(tools), 0)
        self.assertTrue(any(t.name == "Evidently AI" for t in tools))

    def test_pipeline_validation(self):
        engine = OmniAwesomeMLOpsEngine()
        engine.seed_default_tools()
        validator = engine.get_validator()
        
        # Valid logic
        pipe1 = MLOpsPipelineDef("ok_pipe", ["dvc", "mlflow", "seldon", "evidently"])
        res1 = validator.validate_pipeline(pipe1)
        self.assertTrue(is_ok(res1))
        self.assertTrue(unwrap(res1).is_valid)

        # Invalid logic: deployment before training
        pipe2 = MLOpsPipelineDef("bad_pipe", ["seldon", "mlflow"])
        res2 = validator.validate_pipeline(pipe2)
        self.assertTrue(is_ok(res2))
        self.assertFalse(unwrap(res2).is_valid)


class TestEagleEyeEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniEagleEyeEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_extraction_and_matching(self):
        engine = OmniEagleEyeEngine()
        img1 = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
        
        # Extract fake profile
        ext_res = engine.get_extractor().extract(img1, "prof1_img")
        self.assertTrue(is_ok(ext_res))
        
        profile = SocialProfile("instagram", "user123", unwrap(ext_res))
        engine.register_profile(profile)
        
        # Search exact match
        search_res = engine.search_target(img1, threshold=0.99)
        self.assertTrue(is_ok(search_res))
        matches = unwrap(search_res)
        
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].profile.username, "user123")
        self.assertTrue(matches[0].is_verified)


class TestLightFMEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniLightFMEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_sgd_matrix_factorization(self):
        engine = OmniLightFMEngine()
        model = engine.create_model(num_factors=5)
        
        # users x items (3 x 4)
        interactions = np.array([
            [5, 0, 1, 0],
            [0, 4, 0, 5],
            [1, 0, 0, 0]
        ])
        
        # Fit
        fit_res = model.fit(interactions, epochs=5)
        self.assertTrue(is_ok(fit_res))
        
        # Predict known interaction
        pred_res = model.predict(np.array([0]), np.array([0]))
        self.assertTrue(is_ok(pred_res))
        
        # Recommend top 2 for user 1
        rec_res = model.recommend_for_user(1, top_k=2)
        self.assertTrue(is_ok(rec_res))
        recs = unwrap(rec_res)
        self.assertEqual(len(recs), 2)
        
        item_id, score = recs[0]
        # User 1 strongly prefers items 1 and 3
        self.assertIn(item_id, [1, 3])


class TestMarqoEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniMarqoEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_vector_search(self):
        engine = OmniMarqoEngine()
        engine.create_index("test", dimension=3)
        index = unwrap(engine.get_index("test"))
        
        # Add documents
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([0.0, 1.0, 0.0])
        v3 = np.array([0.7, 0.7, 0.0])
        
        index.add_document("doc1", {"title": "Doc 1"}, v1)
        index.add_document("doc2", {"title": "Doc 2"}, v2)
        index.add_document("doc3", {"title": "Doc 3"}, v3)
        
        # Search for something close to v1 using Cosine
        q = np.array([0.9, 0.1, 0.0])
        search_res = index.search(q, top_k=2, method="cosine")
        self.assertTrue(is_ok(search_res))
        
        results = unwrap(search_res)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].document.id, "doc1")
        
        # Search using L2
        search_res_l2 = index.search(q, top_k=2, method="l2")
        self.assertTrue(is_ok(search_res_l2))
        results_l2 = unwrap(search_res_l2)
        self.assertEqual(results_l2[0].document.id, "doc1")

if __name__ == "__main__":
    unittest.main()
