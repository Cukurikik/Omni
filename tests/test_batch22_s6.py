"""
Batch 22 Semester 6 — Integration Test Suite.

Validates all 6 NEW engines:
  1. OmniFedMLEngine         (FedML-AI/FedML)
  2. OmniDeepchecksEngine    (deepchecks/deepchecks)
  3. OmniIGANEngine          (junyanz/iGAN)
  4. OmniLightLLMEngine      (ModelTC/LightLLM)
  5. OmniSurfaceDefectEngine (Charmve/Surface-Defect-Detection)
  6. OmniTorchGeoEngine      (torchgeo/torchgeo)

Tests: ~60 | Zero-algebraic_bound | Pure NumPy
"""
import unittest
import math
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.compute.python_core.omni_fedml_engine import OmniFedMLEngine
from src.compute.python_core.omni_deepchecks_engine import OmniDeepchecksEngine
from src.compute.python_core.omni_igan_engine import OmniIGANEngine
from src.compute.python_core.omni_light_llm_engine import OmniLightLLMEngine
from src.compute.python_core.omni_surface_defect_engine import OmniSurfaceDefectEngine
from src.compute.python_core.omni_torchgeo_engine import OmniTorchGeoEngine


# =========================================================================
#  1. FEDML ENGINE — 10 tests
# =========================================================================

class TestFedMLEngine(unittest.TestCase):
    """Tests for federated learning primitives."""

    def setUp(self):
        self.e = OmniFedMLEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["status"], "operational")

    def test_fedavg_uniform(self):
        w1 = np.array([1.0, 2.0, 3.0])
        w2 = np.array([3.0, 4.0, 5.0])
        res = self.e.fedavg_aggregate_arrays([w1, w2], [100, 100])
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value, [2.0, 3.0, 4.0])

    def test_fedavg_weighted(self):
        w1 = np.array([0.0, 0.0])
        w2 = np.array([4.0, 8.0])
        res = self.e.fedavg_aggregate_arrays([w1, w2], [25, 75])
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value, [3.0, 6.0])

    def test_local_sgd_step(self):
        w = np.array([1.0, 2.0, 3.0])
        g = np.array([0.1, 0.2, 0.3])
        res = self.e.local_sgd_step(w, g, lr=1.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value, [0.9, 1.8, 2.7])

    def test_local_train_epochs(self):
        np.random.seed(0)
        X = np.random.randn(50, 3)
        true_w = np.array([1.0, -2.0, 0.5])
        y = X @ true_w
        init_w = np.zeros(3)
        res = self.e.local_train_epochs(init_w, X, y, lr=0.01, epochs=100)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value["weights"], true_w, atol=0.5)

    def test_partition_dirichlet(self):
        labels = np.array([0]*50 + [1]*50)
        res = self.e.partition_dirichlet(labels, n_clients=5, alpha=0.5)
        self.assertEqual(res.__class__.__name__, "Ok")
        total = sum(len(v) for v in res.value.values())
        self.assertEqual(total, 100)

    def test_partition_iid(self):
        res = self.e.partition_iid(100, 4)
        self.assertEqual(res.__class__.__name__, "Ok")
        total = sum(len(v) for v in res.value.values())
        self.assertEqual(total, 100)

    def test_gaussian_dp(self):
        params = np.ones(10)
        res = self.e.add_gaussian_noise(params, sensitivity=1.0, epsilon=1.0, seed=42)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value["sigma"], 0)
        self.assertEqual(res.value["noisy_params"].shape, params.shape)

    def test_secure_aggregation(self):
        masks_res = self.e.generate_pairwise_masks(3, (5,), seed=0)
        self.assertEqual(masks_res.__class__.__name__, "Ok")
        # Sum of all masks should be ~0
        total_mask = sum(masks_res.value[i] for i in range(3))
        np.testing.assert_allclose(total_mask, 0, atol=1e-10)

    def test_weight_divergence(self):
        gw = np.array([1.0, 2.0, 3.0])
        cw = [np.array([1.1, 2.1, 3.1]), np.array([0.9, 1.9, 2.9])]
        res = self.e.compute_weight_divergence(gw, cw)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value["mean_divergence"], 0)


# =========================================================================
#  2. DEEPCHECKS ENGINE — 10 tests
# =========================================================================

class TestDeepchecksEngine(unittest.TestCase):
    """Tests for ML validation checks."""

    def setUp(self):
        self.e = OmniDeepchecksEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_kl_divergence_same(self):
        p = np.random.RandomState(0).randn(1000)
        res = self.e.kl_divergence(p, p)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 0.0, places=2)

    def test_kl_divergence_different(self):
        p = np.random.RandomState(0).randn(1000)
        q = np.random.RandomState(0).randn(1000) + 5
        res = self.e.kl_divergence(p, q)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value, 0.5)

    def test_psi_no_shift(self):
        data = np.random.RandomState(0).randn(1000)
        res = self.e.psi(data, data + 0.01 * np.random.RandomState(1).randn(1000))
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["interpretation"], "no_shift")

    def test_ks_test(self):
        p = np.random.RandomState(0).randn(500)
        q = np.random.RandomState(1).randn(500) + 3
        res = self.e.ks_test(p, q)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertTrue(res.value["significant"])

    def test_missing_values(self):
        data = np.array([[1, 2], [np.nan, 4], [5, 6]], dtype=np.float64)
        res = self.e.check_missing_values(data)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value["total_pct"], 0)

    def test_duplicates(self):
        data = np.array([[1, 2], [3, 4], [1, 2]], dtype=np.float64)
        res = self.e.check_duplicates(data)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["n_duplicates"], 1)

    def test_permutation_importance(self):
        np.random.seed(42)
        w = np.array([5.0, 0.1, 0.01])
        X = np.random.randn(100, 3)
        y = X @ w
        res = self.e.permutation_importance(w, X, y, n_repeats=5)
        self.assertEqual(res.__class__.__name__, "Ok")
        # Feature 0 should be most important
        self.assertEqual(res.value["ranking"][0], 0)

    def test_performance_comparison(self):
        y_true = np.array([0, 1, 1, 0, 1, 0])
        y_base = np.array([0, 1, 1, 0, 1, 0])  # perfect
        y_new = np.array([0, 0, 1, 0, 1, 0])   # one miss
        res = self.e.performance_comparison(y_true, y_base, y_new)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertTrue(res.value["degraded"])

    def test_check_suite(self):
        data = np.random.RandomState(0).randn(100, 5)
        res = self.e.run_check_suite(data)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertIn("suite_passed", res.value)


# =========================================================================
#  3. iGAN ENGINE — 9 tests
# =========================================================================

class TestIGANEngine(unittest.TestCase):
    """Tests for interactive GAN primitives."""

    def setUp(self):
        self.e = OmniIGANEngine(latent_dim=16)

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_sample_latent(self):
        res = self.e.sample_latent(5, seed=42)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (5, 16))

    def test_lerp(self):
        z1 = np.zeros(16)
        z2 = np.ones(16)
        res = self.e.lerp(z1, z2, 0.5)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value, 0.5 * np.ones(16))

    def test_slerp_endpoints(self):
        z1 = np.random.RandomState(0).randn(16)
        z2 = np.random.RandomState(1).randn(16)
        res0 = self.e.slerp(z1, z2, 0.0)
        res1 = self.e.slerp(z1, z2, 1.0)
        np.testing.assert_allclose(res0.value, z1, atol=1e-10)
        np.testing.assert_allclose(res1.value, z2, atol=1e-10)

    def test_latent_trajectory(self):
        z1 = np.random.RandomState(0).randn(16)
        z2 = np.random.RandomState(1).randn(16)
        res = self.e.latent_trajectory(z1, z2, n_steps=5)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (5, 16))

    def test_generator_linear_block(self):
        z = np.random.RandomState(0).randn(4, 16)
        W = np.random.RandomState(1).randn(32, 16) * 0.1
        b = np.zeros(32)
        res = self.e.generator_linear_block(z, W, b)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (4, 32))
        self.assertTrue(np.all(res.value >= 0))  # ReLU

    def test_bce_loss(self):
        pred = np.array([0.9, 0.1, 0.8])
        target = np.array([1.0, 0.0, 1.0])
        res = self.e.bce_loss(pred, target)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertLess(res.value, 0.5)  # good predictions = low loss

    def test_wasserstein_loss(self):
        real = np.array([1.0, 2.0, 1.5])
        fake = np.array([-1.0, -0.5, -2.0])
        res = self.e.wasserstein_loss(real, fake)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertLess(res.value["d_loss"], 0)  # D_loss should be negative (good)

    def test_spectral_norm(self):
        W = np.random.RandomState(0).randn(8, 8)
        res = self.e.spectral_norm(W, n_power_iterations=10)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value["sigma"], 0)
        # Normalized weight should have spectral norm ≈ 1
        _, s, _ = np.linalg.svd(res.value["normalized_weight"])
        self.assertAlmostEqual(s[0], 1.0, places=1)


# =========================================================================
#  4. LIGHTLLM ENGINE — 10 tests
# =========================================================================

class TestLightLLMEngine(unittest.TestCase):
    """Tests for LLM inference primitives."""

    def setUp(self):
        self.e = OmniLightLLMEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_kv_cache_create_append(self):
        cache = self.e.create_kv_cache(128, 4, 32).value
        self.assertEqual(cache["current_len"], 0)
        new_k = np.random.randn(5, 4, 32)
        new_v = np.random.randn(5, 4, 32)
        res = self.e.append_kv_cache(cache, new_k, new_v)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["current_len"], 5)

    def test_scaled_dot_product_attention(self):
        Q = np.random.RandomState(0).randn(4, 8)
        K = np.random.RandomState(1).randn(6, 8)
        V = np.random.RandomState(2).randn(6, 16)
        res = self.e.scaled_dot_product_attention(Q, K, V)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (4, 16))

    def test_multi_head_attention(self):
        d_model = 16
        n_heads = 4
        Q = np.random.RandomState(0).randn(5, d_model)
        K = np.random.RandomState(1).randn(5, d_model)
        V = np.random.RandomState(2).randn(5, d_model)
        Wq = np.eye(d_model) * 0.1
        Wk = np.eye(d_model) * 0.1
        Wv = np.eye(d_model) * 0.1
        Wo = np.eye(d_model) * 0.1
        res = self.e.multi_head_attention(Q, K, V, n_heads, Wq, Wk, Wv, Wo)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (5, d_model))

    def test_rope_frequencies(self):
        res = self.e.compute_rope_frequencies(head_dim=8, max_seq_len=64)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["cos"].shape, (64, 4))
        self.assertEqual(res.value["sin"].shape, (64, 4))

    def test_apply_rope(self):
        x = np.random.RandomState(0).randn(10, 8)
        rope = self.e.compute_rope_frequencies(8, 64).value
        res = self.e.apply_rope(x, rope["cos"], rope["sin"])
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (10, 8))

    def test_top_k_sampling(self):
        logits = np.array([1.0, 5.0, 3.0, 0.5, 2.0])
        res = self.e.top_k_filter(logits, k=2)
        self.assertEqual(res.__class__.__name__, "Ok")
        # Only top-2 should remain
        finite_count = np.sum(np.isfinite(res.value))
        self.assertEqual(finite_count, 2)

    def test_top_p_sampling(self):
        logits = np.array([10.0, 1.0, 0.1, -5.0, -10.0])
        res = self.e.top_p_filter(logits, p=0.9)
        self.assertEqual(res.__class__.__name__, "Ok")
        # Should keep at least the top token
        self.assertTrue(np.isfinite(res.value[0]))

    def test_quantize_dequantize_int8(self):
        weights = np.array([1.0, -0.5, 0.25, -1.0])
        q_res = self.e.quantize_int8(weights)
        self.assertEqual(q_res.__class__.__name__, "Ok")
        dq_res = self.e.dequantize_int8(q_res.value["quantized"], q_res.value["scale"])
        self.assertEqual(dq_res.__class__.__name__, "Ok")
        np.testing.assert_allclose(dq_res.value, weights, atol=0.02)

    def test_perplexity(self):
        log_probs = np.log(np.array([0.8, 0.7, 0.9, 0.6]))
        res = self.e.compute_perplexity(log_probs)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value, 1.0)


# =========================================================================
#  5. SURFACE DEFECT ENGINE — 10 tests
# =========================================================================

class TestSurfaceDefectEngine(unittest.TestCase):
    """Tests for industrial defect detection primitives."""

    def setUp(self):
        self.e = OmniSurfaceDefectEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_lbp_uniform_image(self):
        img = np.ones((10, 10), dtype=np.float64) * 128
        res = self.e.compute_lbp(img, radius=1)
        self.assertEqual(res.__class__.__name__, "Ok")
        # Uniform image: all neighbors >= center → LBP = 255
        self.assertTrue(np.all(res.value == 255))

    def test_lbp_histogram(self):
        lbp = np.random.RandomState(0).randint(0, 256, (20, 20)).astype(np.uint8)
        res = self.e.compute_lbp_histogram(lbp)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(np.sum(res.value), 1.0)

    def test_glcm_features(self):
        img = np.random.RandomState(0).randint(0, 64, (20, 20))
        glcm_res = self.e.compute_glcm(img, levels=64)
        feats = self.e.glcm_features(glcm_res.value)
        self.assertEqual(feats.__class__.__name__, "Ok")
        self.assertIn("contrast", feats.value)
        self.assertIn("energy", feats.value)
        self.assertGreater(feats.value["energy"], 0)

    def test_mahalanobis(self):
        mean = np.array([0.0, 0.0])
        cov_inv = np.eye(2)
        x = np.array([3.0, 4.0])
        res = self.e.mahalanobis_distance(x, mean, cov_inv)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 5.0)

    def test_morphological_open_close(self):
        binary = np.zeros((10, 10), dtype=np.uint8)
        binary[3:7, 3:7] = 1
        binary[5, 5] = 0  # hole
        closed = self.e.morphological_close(binary, kernel_size=3)
        self.assertEqual(closed.__class__.__name__, "Ok")
        # Closing should fill the hole
        self.assertEqual(closed.value[5, 5], 1)

    def test_sobel_edges(self):
        img = np.zeros((20, 20), dtype=np.float64)
        img[:, 10:] = 255  # vertical edge
        res = self.e.sobel_edges(img)
        self.assertEqual(res.__class__.__name__, "Ok")
        # Max magnitude should be along the edge
        self.assertGreater(np.max(res.value["magnitude"]), 0)

    def test_canny_edge(self):
        img = np.zeros((30, 30), dtype=np.float64)
        img[10:20, 10:20] = 200  # bright square
        res = self.e.canny_edge(img, low_thresh=30, high_thresh=80)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertTrue(np.any(res.value == 1))

    def test_ncc_template_matching(self):
        rng = np.random.RandomState(42)
        image = rng.randint(0, 50, (20, 20)).astype(np.float64)
        # Embed a distinctive bright pattern at (5, 5)
        pattern = np.array([[200, 180, 200, 180, 200],
                            [180, 200, 180, 200, 180],
                            [200, 180, 200, 180, 200],
                            [180, 200, 180, 200, 180],
                            [200, 180, 200, 180, 200]], dtype=np.float64)
        image[5:10, 5:10] = pattern
        res = self.e.normalized_cross_correlation(image, pattern)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["best_loc"], (5, 5))
        self.assertGreater(res.value["best_score"], 0.99)

    def test_cpk(self):
        measurements = np.random.RandomState(0).normal(50, 1, 100)
        res = self.e.compute_cpk(measurements, usl=55, lsl=45)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value["cpk"], 1.0)


# =========================================================================
#  6. TORCHGEO ENGINE — 10 tests
# =========================================================================

class TestTorchGeoEngine(unittest.TestCase):
    """Tests for geospatial data processing."""

    def setUp(self):
        self.e = OmniTorchGeoEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_ndvi(self):
        nir = np.array([[0.8, 0.6], [0.9, 0.7]])
        red = np.array([[0.2, 0.3], [0.1, 0.4]])
        res = self.e.compute_ndvi(nir, red)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertTrue(np.all(res.value > 0))  # vegetation present
        self.assertTrue(np.all(res.value <= 1))

    def test_ndwi(self):
        green = np.array([[0.3, 0.8]])
        nir = np.array([[0.6, 0.2]])
        res = self.e.compute_ndwi(green, nir)
        self.assertEqual(res.__class__.__name__, "Ok")
        # Second pixel: water-dominated (green > nir)
        self.assertGreater(res.value[0, 1], 0)

    def test_savi(self):
        nir = np.ones((2, 2)) * 0.8
        red = np.ones((2, 2)) * 0.2
        res = self.e.compute_savi(nir, red)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertTrue(np.all(res.value > 0))

    def test_evi(self):
        nir = np.ones((2, 2)) * 0.8
        red = np.ones((2, 2)) * 0.2
        blue = np.ones((2, 2)) * 0.1
        res = self.e.compute_evi(nir, red, blue)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertTrue(np.all(res.value > 0))

    def test_haversine(self):
        # Distance from NYC to LA ≈ 3,944 km
        res = self.e.haversine_distance(40.7128, -74.0060, 34.0522, -118.2437)
        self.assertEqual(res.__class__.__name__, "Ok")
        dist_km = res.value / 1000
        self.assertAlmostEqual(dist_km, 3944, delta=100)

    def test_latlon_to_utm(self):
        res = self.e.latlon_to_utm(48.8566, 2.3522)  # Paris
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["zone"], 31)
        self.assertGreater(res.value["easting"], 0)

    def test_grid_sample(self):
        raster = np.random.RandomState(0).rand(20, 20)
        res = self.e.grid_sample(raster, patch_size=5, stride=5)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["n_patches"], 16)  # 4x4 patches

    def test_zonal_stats(self):
        raster = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]], dtype=np.float64)
        zones = np.array([[1, 1, 2], [1, 2, 2], [3, 3, 3]], dtype=int)
        res = self.e.zonal_stats(raster, zones)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertIn(1, res.value)
        self.assertIn(3, res.value)
        self.assertAlmostEqual(res.value[3]["mean"], 8.0)

    def test_cloud_mask(self):
        # Bit 3 set for cloud
        qa = np.array([[0, 8, 0], [8, 0, 8], [0, 0, 0]], dtype=int)
        res = self.e.cloud_mask_from_qa(qa, cloud_bit=3)
        self.assertEqual(res.__class__.__name__, "Ok")
        # Cloud pixels should be 0 (masked)
        self.assertEqual(res.value[0, 1], 0)
        self.assertEqual(res.value[0, 0], 1)  # clear


if __name__ == '__main__':
    unittest.main()
