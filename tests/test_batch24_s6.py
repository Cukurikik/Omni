"""
Batch 24 Semester 6 — Integration Test Suite.

Validates all 6 NEW engines:
  1. OmniNeonEngine               (NervanaSystems/neon)
  2. OmniLitServeEngine           (Lightning-AI/LitServe)
  3. OmniNixtlaEngine             (Nixtla/nixtla)
  4. OmniMatchZooEngine           (NTMC-Community/MatchZoo)
  5. OmniKnowledgeDistillationEngine (dkozlov/awesome-knowledge-distillation)
  6. OmniFIDEngine                (mseitzer/pytorch-fid)

Tests: ~60 | Zero-algebraic_bound | Pure NumPy
"""
import unittest
import math
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.compute.python_core.omni_neon_engine import OmniNeonEngine
from src.compute.python_core.omni_litserve_engine import (
    OmniLitServeEngine, InferenceRequest, InferenceResponse,
)
from src.compute.python_core.omni_nixtla_engine import OmniNixtlaEngine
from src.compute.python_core.omni_matchzoo_engine import OmniMatchZooEngine
from src.compute.python_core.omni_knowledge_distillation_engine import OmniKnowledgeDistillationEngine
from src.compute.python_core.omni_fid_engine import OmniFIDEngine


# =========================================================================
#  1. NEON ENGINE — 10 tests
# =========================================================================

class TestNeonEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniNeonEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_gemm(self):
        A = np.random.RandomState(0).randn(3, 4)
        B = np.random.RandomState(1).randn(4, 5)
        res = self.e.gemm(A, B, alpha=2.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (3, 5))

    def test_xavier_init(self):
        res = self.e.xavier_init(100, 50)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (100, 50))
        limit = math.sqrt(6.0 / 150)
        self.assertLess(np.max(np.abs(res.value)), limit + 0.01)

    def test_he_init(self):
        res = self.e.he_init(100, 50)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (100, 50))

    def test_linear_forward_backward(self):
        x = np.random.RandomState(0).randn(8, 10)
        W = np.random.RandomState(1).randn(10, 5) * 0.1
        b = np.zeros(5)
        fwd = self.e.linear_forward(x, W, b)
        self.assertEqual(fwd.value.shape, (8, 5))
        grad_out = np.ones((8, 5))
        bwd = self.e.linear_backward(grad_out, x, W)
        self.assertEqual(bwd.value["grad_W"].shape, (10, 5))

    def test_batchnorm(self):
        x = np.random.RandomState(0).randn(16, 8)
        gamma = np.ones(8)
        beta = np.zeros(8)
        res = self.e.batchnorm_forward(x, gamma, beta)
        self.assertEqual(res.__class__.__name__, "Ok")
        # Normalized output should be ~zero mean, ~unit var
        self.assertAlmostEqual(np.mean(res.value["output"]), 0.0, delta=0.1)

    def test_dropout(self):
        x = np.ones((10, 10))
        res = self.e.dropout(x, p=0.5, training=True, seed=0)
        self.assertLess(np.sum(res.value["mask"]), 100)

    def test_relu_sigmoid(self):
        x = np.array([-2, -1, 0, 1, 2], dtype=float)
        relu_res = self.e.relu(x)
        np.testing.assert_array_equal(relu_res.value[:3], [0, 0, 0])
        sig_res = self.e.sigmoid(np.array([0.0]))
        self.assertAlmostEqual(sig_res.value[0], 0.5)

    def test_adam_step(self):
        param = np.ones(5)
        grad = np.ones(5) * 0.1
        m = np.zeros(5)
        v = np.zeros(5)
        res = self.e.adam_step(param, grad, m, v, t=1)
        self.assertEqual(res.__class__.__name__, "Ok")
        # Parameter should decrease
        self.assertTrue(np.all(res.value["param"] < param))

    def test_gradient_clip(self):
        grads = [np.ones(10) * 10]
        res = self.e.gradient_clip_norm(grads, max_norm=1.0)
        total = math.sqrt(float(np.sum(res.value[0] ** 2)))
        self.assertAlmostEqual(total, 1.0, places=3)


# =========================================================================
#  2. LITSERVE ENGINE — 10 tests
# =========================================================================

class TestLitServeEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniLitServeEngine(max_batch_size=4, timeout_ms=50)

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_validate_request(self):
        payload = np.array([1.0, 2.0, 3.0])
        res = self.e.validate_request(payload)
        self.assertEqual(res.__class__.__name__, "Ok")
        # NaN should fail
        bad = np.array([1.0, float('nan')])
        res2 = self.e.validate_request(bad)
        self.assertEqual(res2.__class__.__name__, "Err")

    def test_preprocess(self):
        payload = np.array([0.0, 100.0, 200.0])
        res = self.e.preprocess(payload, normalize=True)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(np.mean(res.value), 0.0, places=5)

    def test_postprocess_softmax(self):
        logits = np.array([2.0, 1.0, 0.1])
        res = self.e.postprocess(logits, apply_softmax=True)
        self.assertAlmostEqual(np.sum(res.value), 1.0, places=5)

    def test_batch_requests(self):
        reqs = [
            InferenceRequest(request_id=f"r{i}", payload=np.ones(5) * i)
            for i in range(3)
        ]
        res = self.e.batch_requests(reqs)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["batch_tensor"].shape, (3, 5))

    def test_batch_exceed_max(self):
        reqs = [InferenceRequest(f"r{i}", np.ones(2)) for i in range(5)]
        res = self.e.batch_requests(reqs)
        self.assertEqual(res.__class__.__name__, "Err")

    def test_unbatch_responses(self):
        batch = np.random.randn(3, 4)
        ids = ["a", "b", "c"]
        res = self.e.unbatch_responses(batch, ids, latency_ms=30.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(len(res.value), 3)
        self.assertAlmostEqual(res.value[0].latency_ms, 10.0)

    def test_stream_generate(self):
        state = np.random.RandomState(0).randn(16)
        W = np.random.RandomState(1).randn(16, 50) * 0.1
        res = self.e.stream_generate(state, n_steps=5, W_proj=W, seed=42)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(len(res.value), 5)

    def test_health_readiness(self):
        h = self.e.health_check()
        r = self.e.readiness_check(model_loaded=True)
        self.assertEqual(h.value["status"], "healthy")
        self.assertEqual(r.value["status"], "ready")

    def test_metrics(self):
        # Process some requests to generate metrics
        reqs = [InferenceRequest(f"r{i}", np.ones(3)) for i in range(2)]
        batch_res = self.e.batch_requests(reqs)
        batch_out = np.random.randn(2, 3)
        self.e.unbatch_responses(batch_out, ["r0", "r1"], latency_ms=20.0)
        m = self.e.get_metrics()
        self.assertEqual(m.__class__.__name__, "Ok")
        self.assertEqual(m.value.total_requests, 2)


# =========================================================================
#  3. NIXTLA ENGINE — 10 tests
# =========================================================================

class TestNixtlaEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniNixtlaEngine()
        np.random.seed(42)
        self.ts = np.sin(np.linspace(0, 4 * np.pi, 100)) + np.random.randn(100) * 0.1

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_naive_forecast(self):
        res = self.e.naive_forecast(self.ts, horizon=10)
        self.assertEqual(len(res.value), 10)
        np.testing.assert_allclose(res.value, self.ts[-1])

    def test_seasonal_naive(self):
        res = self.e.seasonal_naive(self.ts, horizon=25, season_length=25)
        self.assertEqual(len(res.value), 25)

    def test_exponential_smoothing(self):
        res = self.e.exponential_smoothing(self.ts, horizon=5, alpha=0.3)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(len(res.value["forecast"]), 5)
        self.assertEqual(len(res.value["fitted"]), len(self.ts))

    def test_decompose(self):
        res = self.e.decompose(self.ts, period=25)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(len(res.value["trend"]), len(self.ts))

    def test_lag_features(self):
        res = self.e.lag_features(self.ts, lags=[1, 7])
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (100, 2))

    def test_anomaly_zscore(self):
        series = np.zeros(50)
        series[25] = 100  # clear anomaly
        res = self.e.anomaly_zscore(series, threshold=3.0)
        self.assertTrue(res.value["is_anomaly"][25])

    def test_anomaly_iqr(self):
        series = np.random.RandomState(0).randn(100)
        series[50] = 50.0  # clear outlier
        res = self.e.anomaly_iqr(series)
        self.assertTrue(res.value["is_anomaly"][50])

    def test_metrics(self):
        actual = np.array([1.0, 2.0, 3.0, 4.0])
        pred = np.array([1.1, 2.2, 2.8, 4.1])
        mae = self.e.mae(actual, pred)
        rmse = self.e.rmse(actual, pred)
        self.assertLess(mae.value, 0.5)
        self.assertLess(rmse.value, 0.5)

    def test_conformal_interval(self):
        residuals = np.random.RandomState(0).randn(100)
        forecast = np.ones(10) * 5.0
        res = self.e.conformal_interval(residuals, forecast, alpha=0.1)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertTrue(np.all(res.value["upper"] > res.value["lower"]))


# =========================================================================
#  4. MATCHZOO ENGINE — 10 tests
# =========================================================================

class TestMatchZooEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniMatchZooEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_tf(self):
        res = self.e.compute_tf(["the", "cat", "sat", "the"])
        self.assertAlmostEqual(res.value["the"], 0.5)

    def test_idf(self):
        corpus = [["cat", "dog"], ["dog", "bird"], ["cat", "bird", "dog"]]
        res = self.e.compute_idf(corpus)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertIn("cat", res.value)

    def test_tfidf_vector(self):
        corpus = [["cat", "dog"], ["dog", "bird"]]
        idf_res = self.e.compute_idf(corpus)
        vocab = ["cat", "dog", "bird"]
        res = self.e.tfidf_vector(["cat", "dog"], idf_res.value, vocab)
        self.assertEqual(res.value.shape, (3,))

    def test_bm25(self):
        corpus = [["cat", "dog"], ["dog", "bird"], ["fish", "bird"]]
        idf_res = self.e.compute_idf(corpus)
        res = self.e.bm25_score(["cat"], ["cat", "dog", "cat"], idf_res.value, avgdl=2.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value, 0)

    def test_cosine_interaction(self):
        q = np.random.RandomState(0).randn(3, 16)
        d = np.random.RandomState(1).randn(5, 16)
        res = self.e.cosine_interaction_matrix(q, d)
        self.assertEqual(res.value.shape, (3, 5))
        self.assertTrue(np.all(res.value >= -1.01) and np.all(res.value <= 1.01))

    def test_knrm_kernels(self):
        im = np.random.RandomState(0).rand(3, 5) * 2 - 1  # cosine range
        res = self.e.knrm_kernels(im, n_kernels=11)
        self.assertEqual(res.value.shape, (3, 11))

    def test_drmm_matching(self):
        im = np.random.RandomState(0).rand(4, 6) * 2 - 1
        res = self.e.drmm_matching(im, n_bins=10)
        self.assertEqual(res.value.shape, (4, 10))

    def test_pairwise_hinge(self):
        pos = np.array([0.9, 0.8, 0.7])
        neg = np.array([0.1, 0.2, 0.3])
        res = self.e.pairwise_hinge_loss(pos, neg, margin=0.3)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 0.0)  # all margins satisfied

    def test_ndcg(self):
        rel = np.array([3, 2, 1, 0, 0])
        res = self.e.ndcg(rel.astype(float))
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value, 0.9)  # already sorted


# =========================================================================
#  5. KNOWLEDGE DISTILLATION ENGINE — 10 tests
# =========================================================================

class TestKnowledgeDistillationEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniKnowledgeDistillationEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_soft_targets(self):
        logits = np.array([2.0, 1.0, 0.1])
        # T=1: sharp
        res1 = self.e.soft_targets(logits, temperature=1.0)
        # T=10: soft
        res10 = self.e.soft_targets(logits, temperature=10.0)
        # Higher T → more uniform
        self.assertGreater(np.std(res1.value), np.std(res10.value))

    def test_kl_divergence_same(self):
        p = np.array([0.2, 0.3, 0.5])
        res = self.e.kl_divergence(p, p)
        self.assertAlmostEqual(res.value, 0.0, places=5)

    def test_distillation_loss(self):
        t_logits = np.array([[2.0, 1.0, 0.1], [0.1, 3.0, 0.5]])
        s_logits = np.array([[1.5, 0.8, 0.2], [0.3, 2.5, 0.6]])
        res = self.e.distillation_loss(t_logits, s_logits, temperature=4.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value, 0)

    def test_combined_loss(self):
        t_logits = np.array([[2.0, 0.5], [0.5, 2.0]])
        s_logits = np.array([[1.5, 0.8], [0.8, 1.5]])
        targets = np.array([0, 1])
        res = self.e.combined_loss(t_logits, s_logits, targets, temperature=3.0, alpha=0.7)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value["total"], 0)

    def test_feature_distillation(self):
        t_feat = np.random.RandomState(0).randn(8, 64)
        s_feat = np.random.RandomState(1).randn(8, 32)
        W = np.random.RandomState(2).randn(32, 64) * 0.1
        res = self.e.feature_distillation_loss(t_feat, s_feat, W_transform=W)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value, 0)

    def test_attention_map(self):
        fmap = np.random.RandomState(0).randn(16, 8, 8)
        res = self.e.attention_map(fmap)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (8, 8))
        self.assertAlmostEqual(np.sum(res.value), 1.0, places=5)

    def test_attention_transfer(self):
        t_fmap = np.random.RandomState(0).randn(32, 8, 8)
        s_fmap = np.random.RandomState(1).randn(16, 8, 8)
        res = self.e.attention_transfer_loss(t_fmap, s_fmap)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value, 0)

    def test_ensemble_soft_targets(self):
        t1 = np.array([[3.0, 1.0, 0.5]])
        t2 = np.array([[2.0, 2.0, 0.5]])
        res = self.e.ensemble_soft_targets([t1, t2], temperature=3.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(np.sum(res.value), 1.0, places=5)

    def test_progressive_schedule(self):
        res_start = self.e.progressive_temperature_schedule(0, 100, 10.0, 1.0)
        res_end = self.e.progressive_temperature_schedule(100, 100, 10.0, 1.0)
        self.assertAlmostEqual(res_start.value, 10.0)
        self.assertAlmostEqual(res_end.value, 1.0)


# =========================================================================
#  6. FID ENGINE — 10 tests
# =========================================================================

class TestFIDEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniFIDEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_compute_statistics(self):
        features = np.random.RandomState(0).randn(100, 16)
        res = self.e.compute_statistics(features)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["mu"].shape, (16,))
        self.assertEqual(res.value["sigma"].shape, (16, 16))

    def test_matrix_sqrt(self):
        M = np.eye(4) * 4.0
        res = self.e.matrix_sqrt_newton(M)
        self.assertEqual(res.__class__.__name__, "Ok")
        # sqrt(4I) = 2I
        np.testing.assert_allclose(res.value, np.eye(4) * 2.0, atol=1e-5)

    def test_fid_same_distribution(self):
        rng = np.random.RandomState(0)
        features = rng.randn(200, 8)
        res = self.e.compute_fid(features, features)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertLess(res.value, 1.0)  # near zero for same data

    def test_fid_different_distributions(self):
        rng = np.random.RandomState(0)
        real = rng.randn(200, 8)
        gen = rng.randn(200, 8) + 5  # shifted distribution
        res = self.e.compute_fid(real, gen)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value, 10.0)  # large FID for different distributions

    def test_inception_score(self):
        # Diverse predictions → higher IS
        rng = np.random.RandomState(0)
        n_classes = 10
        probs_diverse = np.zeros((100, n_classes))
        for i in range(100):
            probs_diverse[i, i % n_classes] = 1.0  # one-hot → max diversity
        # Smooth slightly to avoid log(0)
        probs_diverse = probs_diverse * 0.99 + 0.01 / n_classes
        probs_diverse /= probs_diverse.sum(axis=1, keepdims=True)
        res = self.e.inception_score(probs_diverse)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value["mean"], 1.0)

    def test_kid(self):
        rng = np.random.RandomState(0)
        real = rng.randn(100, 8)
        gen = rng.randn(100, 8)
        res = self.e.kernel_inception_distance(real, gen, n_subsets=3, subset_size=50)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertIn("mean", res.value)

    def test_perceptual_distance_same(self):
        features = np.random.RandomState(0).randn(10, 16)
        res = self.e.perceptual_distance(features, features)
        self.assertAlmostEqual(res.value, 0.0, places=5)

    def test_perceptual_distance_diff(self):
        a = np.random.RandomState(0).randn(10, 16)
        b = np.random.RandomState(1).randn(10, 16)
        res = self.e.perceptual_distance(a, b)
        self.assertGreater(res.value, 0)

    def test_polynomial_kernel(self):
        x = np.random.RandomState(0).randn(5, 8)
        y = np.random.RandomState(1).randn(3, 8)
        res = self.e.polynomial_kernel(x, y, degree=3)
        self.assertEqual(res.value.shape, (5, 3))


if __name__ == '__main__':
    unittest.main()
