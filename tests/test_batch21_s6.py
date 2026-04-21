"""
Batch 21 Semester 6 — Integration Test Suite.

Validates all 6 engines covering 6 open-source repository knowledge domains:
  1. OmniDataScienceRoadmapEngine  (Moataz-Elmesmary/Data-Science-Roadmap)
  2. OmniNeuralProphetEngine       (ourownstory/neural_prophet)
  3. OmniDeepFilterNetEngine       (Rikorose/DeepFilterNet)
  4. OmniHLocEngine                (cvg/Hierarchical-Localization)
  5. Omni3DResNetEngine            (kenshohara/3D-ResNets-PyTorch)
  6. OmniDeepXDEEngine             (lululxvi/deepxde)

Tests: ~65 | Zero-algebraic_bound | Pure NumPy
"""
import unittest
import math
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.compute.python_core.omni_data_science_roadmap_engine import OmniDataScienceRoadmapEngine
from src.compute.python_core.omni_neural_prophet_engine import OmniNeuralProphetEngine
from src.compute.python_core.omni_deep_filter_net_engine import OmniDeepFilterNetEngine
from src.compute.python_core.omni_hloc_engine import OmniHLocEngine
from src.compute.python_core.omni_3d_resnet_engine import Omni3DResNetEngine
from src.compute.python_core.omni_deepxde_engine import OmniDeepXDEEngine


# =========================================================================
#  1. DATA SCIENCE ROADMAP ENGINE — 20 tests
# =========================================================================

class TestDataScienceRoadmapEngine(unittest.TestCase):
    """Tests covering statistics, probability, linalg, cleaning, features, metrics."""

    def setUp(self):
        self.e = OmniDataScienceRoadmapEngine()

    # --- Descriptive Statistics ---
    def test_mean(self):
        res = self.e.mean(np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 3.0)

    def test_median_odd(self):
        res = self.e.median(np.array([1, 3, 5, 7, 9], dtype=np.float64))
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 5.0)

    def test_mode(self):
        res = self.e.mode(np.array([1, 2, 2, 3, 3, 3, 4]))
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["mode"], 3.0)
        self.assertEqual(res.value["count"], 3)

    def test_variance_population(self):
        res = self.e.variance(np.array([2, 4, 4, 4, 5, 5, 7, 9], dtype=np.float64))
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 4.0)

    def test_std_sample(self):
        data = np.array([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
        res = self.e.std(data, ddof=1)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, math.sqrt(np.var(data, ddof=1)), places=10)

    def test_skewness_symmetric(self):
        data = np.array([-2, -1, 0, 1, 2], dtype=np.float64)
        res = self.e.skewness(data)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 0.0, places=10)

    def test_kurtosis_uniform(self):
        np.random.seed(42)
        data = np.random.uniform(0, 1, 10000)
        res = self.e.kurtosis(data)
        self.assertEqual(res.__class__.__name__, "Ok")
        # Uniform excess kurtosis ≈ -1.2
        self.assertAlmostEqual(res.value, -1.2, places=1)

    def test_percentiles(self):
        data = np.arange(101, dtype=np.float64)
        res = self.e.percentiles(data, [25, 50, 75])
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value[50], 50.0)

    # --- Probability ---
    def test_bayes_theorem(self):
        # P(disease|positive) = P(positive|disease)*P(disease) / P(positive)
        res = self.e.bayes(prior=0.01, likelihood=0.99, evidence=0.05)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 0.198, places=3)

    def test_binomial_pmf(self):
        # P(X=3) for n=5, p=0.5
        res = self.e.binomial(5, 3, 0.5)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 0.3125, places=4)

    def test_poisson_pmf(self):
        # P(X=2) for lambda=3
        res = self.e.poisson(3.0, 2)
        self.assertEqual(res.__class__.__name__, "Ok")
        expected = (3**2 * math.exp(-3)) / math.factorial(2)
        self.assertAlmostEqual(res.value, expected, places=10)

    # --- Linear Algebra ---
    def test_determinant(self):
        A = np.array([[1, 2], [3, 4]], dtype=np.float64)
        res = self.e.determinant(A)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, -2.0, places=10)

    def test_eigenvalues(self):
        A = np.array([[2, 0], [0, 3]], dtype=np.float64)
        res = self.e.eigenvalues(A)
        self.assertEqual(res.__class__.__name__, "Ok")
        evals = sorted(res.value["eigenvalues"].real)
        self.assertAlmostEqual(evals[0], 2.0)
        self.assertAlmostEqual(evals[1], 3.0)

    def test_svd_reconstruction(self):
        A = np.random.RandomState(0).rand(4, 3)
        res = self.e.svd(A)
        self.assertEqual(res.__class__.__name__, "Ok")
        reconstructed = res.value["U"] @ np.diag(res.value["S"]) @ res.value["Vt"]
        np.testing.assert_allclose(A, reconstructed, atol=1e-10)

    def test_pseudoinverse(self):
        A = np.array([[1, 2], [3, 4], [5, 6]], dtype=np.float64)
        res = self.e.pseudoinverse(A)
        self.assertEqual(res.__class__.__name__, "Ok")
        identity_approx = res.value @ A
        np.testing.assert_allclose(identity_approx, np.eye(2), atol=1e-10)

    # --- Data Cleaning ---
    def test_outliers_iqr(self):
        data = np.array([1, 2, 3, 4, 5, 100], dtype=np.float64)
        res = self.e.outliers_iqr(data)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertTrue(res.value["mask"][-1])  # 100 is outlier
        self.assertFalse(res.value["mask"][2])   # 3 is not

    def test_impute_mean(self):
        data = np.array([[1, 2], [3, np.nan], [5, 6]], dtype=np.float64)
        res = self.e.impute_mean(data)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value[1, 1], 4.0)  # mean of [2, 6]

    # --- Feature Engineering ---
    def test_min_max_scale(self):
        data = np.array([[0], [5], [10]], dtype=np.float64)
        res = self.e.min_max_scale(data)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value["scaled"], [[0], [0.5], [1.0]])

    def test_one_hot_encode(self):
        labels = np.array([0, 1, 2, 1])
        res = self.e.one_hot_encode(labels)
        self.assertEqual(res.__class__.__name__, "Ok")
        expected = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 1, 0]], dtype=np.float64)
        np.testing.assert_array_equal(res.value, expected)

    # --- Evaluation Metrics ---
    def test_accuracy(self):
        y_true = np.array([0, 1, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 0, 1])
        res = self.e.accuracy(y_true, y_pred)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 0.8)

    def test_precision_recall_f1(self):
        y_true = np.array([1, 1, 0, 0, 1, 0])
        y_pred = np.array([1, 0, 0, 0, 1, 1])
        res = self.e.precision_recall_f1(y_true, y_pred)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value["precision"], 2 / 3, places=5)
        self.assertAlmostEqual(res.value["recall"], 2 / 3, places=5)

    def test_roc_auc_perfect(self):
        y_true = np.array([0, 0, 1, 1])
        y_scores = np.array([0.1, 0.4, 0.6, 0.9])
        res = self.e.roc_auc(y_true, y_scores)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 1.0)

    def test_mse(self):
        y_true = np.array([1.0, 2.0, 3.0])
        y_pred = np.array([1.0, 2.0, 3.0])
        res = self.e.mse(y_true, y_pred)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 0.0)

    def test_r_squared_perfect(self):
        y = np.array([1.0, 2.0, 3.0, 4.0])
        res = self.e.r_squared(y, y)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 1.0)

    def test_correlation_matrix(self):
        data = np.array([[1, 2], [2, 4], [3, 6]], dtype=np.float64)
        res = self.e.correlation_matrix(data)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value, np.ones((2, 2)), atol=1e-10)


# =========================================================================
#  2. NEURAL PROPHET ENGINE — 8 tests
# =========================================================================

class TestNeuralProphetEngine(unittest.TestCase):
    """Tests for time series decomposition engine."""

    def setUp(self):
        self.e = OmniNeuralProphetEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["status"], "active")

    def test_linear_trend(self):
        t = np.linspace(0, 1, 50)
        y = 2.5 * t + 1.0 + np.random.RandomState(0).randn(50) * 0.01
        res = self.e.fit_linear_trend(t, y)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value["slope"], 2.5, places=1)
        self.assertAlmostEqual(res.value["intercept"], 1.0, places=1)

    def test_piecewise_trend(self):
        t = np.linspace(0, 1, 100)
        y = np.where(t < 0.5, 2 * t, 2 * 0.5 + 0.5 * (t - 0.5))
        cp = np.array([0.5])
        res = self.e.fit_piecewise_trend(t, y, cp)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value["trend"], y, atol=0.1)

    def test_fourier_seasonality_shape(self):
        t = np.arange(365, dtype=np.float64)
        res = self.e.fourier_seasonality(t, period=365.25, n_harmonics=5)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (365, 10))

    def test_fit_seasonality(self):
        t = np.arange(200, dtype=np.float64)
        seasonal = np.sin(2 * np.pi * t / 50)
        res = self.e.fit_seasonality(t, seasonal, period=50, n_harmonics=3)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value["seasonal"], seasonal, atol=0.05)

    def test_autoregressive(self):
        np.random.seed(42)
        y = np.cumsum(np.random.randn(100))
        res = self.e.autoregressive_predict(y, ar_order=3)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(len(res.value["coefficients"]), 3)
        self.assertEqual(len(res.value["fitted"]), 97)

    def test_detect_changepoints(self):
        y = np.random.RandomState(0).rand(200)
        res = self.e.detect_changepoints(y, n_changepoints=5)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(len(res.value), 5)

    def test_invalid_trend(self):
        res = self.e.fit_linear_trend(np.array([1]), np.array([2]))
        self.assertEqual(res.__class__.__name__, "Err")


# =========================================================================
#  3. DEEPFILTERNET ENGINE — 15 tests
# =========================================================================

class TestDeepFilterNetEngine(unittest.TestCase):
    """Tests for full-band speech enhancement primitives."""

    def setUp(self):
        self.e = OmniDeepFilterNetEngine(n_fft=256, hop_length=64, sr=16000)

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["status"], "operational")

    def test_stft_shape(self):
        signal = np.random.RandomState(0).randn(4096)
        res = self.e.stft(signal)
        self.assertEqual(res.__class__.__name__, "Ok")
        n_bins = self.e.n_fft // 2 + 1
        n_frames = 1 + (len(signal) - self.e.n_fft) // self.e.hop_length
        self.assertEqual(res.value.shape, (n_frames, n_bins))

    def test_stft_istft_roundtrip(self):
        signal = np.random.RandomState(1).randn(4096)
        stft_res = self.e.stft(signal)
        istft_res = self.e.istft(stft_res.value, output_length=len(signal))
        self.assertEqual(istft_res.__class__.__name__, "Ok")
        # Check interior (trim edge effects)
        trim = self.e.hop_length
        np.testing.assert_allclose(
            istft_res.value[trim:-trim], signal[trim:-trim], atol=1e-6
        )

    def test_erb_filterbank_shape(self):
        res = self.e.erb_filterbank(n_erb_bands=32)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (32, self.e.n_fft // 2 + 1))

    def test_erb_filterbank_sums(self):
        res = self.e.erb_filterbank(n_erb_bands=16)
        fb = res.value
        # Each band should sum to 1.0 (or 0 for empty bands)
        for b in range(fb.shape[0]):
            s = np.sum(fb[b])
            if s > 0:
                self.assertAlmostEqual(s, 1.0, places=8)

    def test_apply_erb_filterbank(self):
        sig = np.random.RandomState(2).randn(2048)
        spec = self.e.stft(sig).value
        power = np.abs(spec) ** 2
        fb = self.e.erb_filterbank(16).value
        res = self.e.apply_erb_filterbank(power, fb)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape[0], power.shape[0])
        self.assertEqual(res.value.shape[1], 16)

    def test_deep_filter(self):
        n_frames, n_bins, filt_len = 20, 10, 3
        noisy = np.random.RandomState(3).randn(n_frames, n_bins) + 0j
        coeffs = np.zeros((n_frames, n_bins, filt_len), dtype=np.complex128)
        coeffs[:, :, 0] = 1.0  # identity filter
        res = self.e.deep_filter(noisy, coeffs)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value, noisy, atol=1e-10)

    def test_ideal_ratio_mask(self):
        clean = np.array([[1 + 0j, 2 + 0j], [3 + 0j, 4 + 0j]])
        noisy = clean + 0.5  # add noise
        res = self.e.ideal_ratio_mask(clean, noisy)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertTrue(np.all(res.value >= 0) and np.all(res.value <= 1))

    def test_wiener_gain(self):
        noisy_power = np.array([[10.0, 5.0], [8.0, 1.0]])
        noise_power = np.array([[2.0, 4.0], [1.0, 0.5]])
        res = self.e.wiener_gain(noisy_power, noise_power, floor=0.01)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertTrue(np.all(res.value >= 0.01))
        self.assertTrue(np.all(res.value <= 1.0))

    def test_apply_spectral_gain(self):
        spec = np.array([[1 + 1j, 2 + 2j]])
        gain = np.array([[0.5, 1.0]])
        res = self.e.apply_spectral_gain(spec, gain)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value, [[0.5 + 0.5j, 2 + 2j]])

    def test_noise_psd_estimation(self):
        np.random.seed(5)
        noise = np.random.randn(50, 10) ** 2
        res = self.e.estimate_noise_psd(noise, alpha=0.95, initial_frames=5)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, noise.shape)
        self.assertTrue(np.all(res.value >= 0))

    def test_post_filter(self):
        gain = np.array([[0.0, 0.5, 1.0], [0.01, 0.3, 0.9]])
        res = self.e.post_filter(gain, beta=0.02)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertTrue(np.all(res.value >= 0) and np.all(res.value <= 1.0))
        # Post-filter should reduce low-gain regions more
        self.assertLess(res.value[0, 0], 0.01)

    def test_band_split_merge_roundtrip(self):
        spec = np.random.RandomState(6).randn(10, 50) + 0j
        split_res = self.e.band_split(spec, df_bins=20)
        self.assertEqual(split_res.__class__.__name__, "Ok")
        merge_res = self.e.band_merge(split_res.value["df_band"], split_res.value["erb_band"])
        self.assertEqual(merge_res.__class__.__name__, "Ok")
        np.testing.assert_allclose(merge_res.value, spec)

    def test_compute_snr(self):
        clean = np.sin(2 * np.pi * 440 * np.linspace(0, 0.1, 1600))
        noise = np.random.RandomState(7).randn(1600) * 0.01
        noisy = clean + noise
        res = self.e.compute_snr(clean, noisy)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value, 20)  # should be > 20 dB

    def test_enhance_wiener_pipeline(self):
        clean = np.sin(2 * np.pi * 440 * np.linspace(0, 0.5, 8000))
        noise = np.random.RandomState(8).randn(8000) * 0.05
        noisy = clean + noise
        res = self.e.enhance_wiener(noisy, floor=0.01)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(len(res.value["enhanced"]), len(noisy))


# =========================================================================
#  4. HLOC ENGINE — 6 tests
# =========================================================================

class TestHLocEngine(unittest.TestCase):
    """Tests for visual localization primitives."""

    def setUp(self):
        self.e = OmniHLocEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_harris_corner_response(self):
        # Checkerboard has strong corners
        img = np.zeros((20, 20), dtype=np.float64)
        img[:10, :10] = 1.0
        img[10:, 10:] = 1.0
        res = self.e.harris_corner_response(img)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, img.shape)

    def test_extract_keypoints(self):
        img = np.zeros((30, 30), dtype=np.float64)
        img[10, 10] = 10.0  # bright point
        img[20, 20] = 10.0
        response = self.e.harris_corner_response(img).value
        res = self.e.extract_keypoints(response, threshold=0.01)
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_descriptor_matching(self):
        np.random.seed(10)
        desc_a = np.random.rand(5, 32)
        desc_b = np.vstack([desc_a[:3] + 0.01 * np.random.rand(3, 32), np.random.rand(5, 32)])
        res = self.e.match_descriptors_ratio_test(desc_a, desc_b, ratio_thresh=0.8)
        self.assertEqual(res.__class__.__name__, "Ok")
        # Should find at least some matches for the near-duplicate descriptors
        self.assertGreater(len(res.value), 0)

    def test_homography_dlt(self):
        src = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float64)
        # Identity transform
        dst = src.copy()
        res = self.e.estimate_homography_dlt(src, dst)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value, np.eye(3), atol=1e-5)

    def test_reprojection_error(self):
        src = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float64)
        H = np.eye(3)
        res = self.e.compute_reprojection_error(src, src, H)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value, np.zeros(4), atol=1e-10)


# =========================================================================
#  5. 3D RESNET ENGINE — 5 tests
# =========================================================================

class TestResNet3DEngine(unittest.TestCase):
    """Tests for spatiotemporal convolution primitives."""

    def setUp(self):
        self.e = Omni3DResNetEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_conv3d_identity(self):
        # 3x3x3 kernel with center=1 should reproduce input (with trimming)
        inp = np.random.RandomState(0).rand(8, 8, 8)
        kernel = np.zeros((3, 3, 3))
        kernel[1, 1, 1] = 1.0
        res = self.e.conv3d(inp, kernel, padding=(1, 1, 1))
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value, inp, atol=1e-10)

    def test_batch_norm_5d(self):
        tensor = np.random.RandomState(1).randn(2, 3, 4, 4, 4)
        gamma = np.ones(3)
        beta = np.zeros(3)
        res = self.e.batch_norm_5d(tensor, gamma, beta)
        self.assertEqual(res.__class__.__name__, "Ok")
        # Normalized channels should have ~0 mean
        for c in range(3):
            channel_mean = np.mean(res.value[:, c, :, :, :])
            self.assertAlmostEqual(channel_mean, 0.0, places=10)

    def test_residual_add(self):
        x = np.array([1.0, -2.0, 3.0])
        shortcut = np.array([0.0, 3.0, -1.0])
        res = self.e.residual_add(x, shortcut)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_array_equal(res.value, [1.0, 1.0, 2.0])

    def test_global_avg_pool_3d(self):
        tensor = np.ones((2, 4, 3, 3, 3))
        res = self.e.global_avg_pool_3d(tensor)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (2, 4))
        np.testing.assert_allclose(res.value, 1.0)


# =========================================================================
#  6. DEEPXDE ENGINE — 7 tests
# =========================================================================

class TestDeepXDEEngine(unittest.TestCase):
    """Tests for physics-informed neural network primitives."""

    def setUp(self):
        self.e = OmniDeepXDEEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_finite_diff_1st_order(self):
        x = np.linspace(0, 2 * np.pi, 100)
        f = np.sin(x)
        dx = x[1] - x[0]
        res = self.e.finite_diff_gradient(f, dx, order=1)
        self.assertEqual(res.__class__.__name__, "Ok")
        expected = np.cos(x[1:-1])
        np.testing.assert_allclose(res.value, expected, atol=0.01)

    def test_finite_diff_2nd_order(self):
        x = np.linspace(0, 2 * np.pi, 200)
        f = np.sin(x)
        dx = x[1] - x[0]
        res = self.e.finite_diff_gradient(f, dx, order=2)
        self.assertEqual(res.__class__.__name__, "Ok")
        expected = -np.sin(x[1:-1])
        np.testing.assert_allclose(res.value, expected, atol=0.01)

    def test_collocation_uniform(self):
        bounds = np.array([[0, 1], [0, 1]], dtype=np.float64)
        res = self.e.sample_collocation_uniform(bounds, 100)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (100, 2))
        self.assertTrue(np.all(res.value >= 0) and np.all(res.value <= 1))

    def test_collocation_lhs(self):
        bounds = np.array([[0, 1], [0, 1]], dtype=np.float64)
        res = self.e.sample_collocation_lhs(bounds, 50)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (50, 2))

    def test_poisson_residual_zero(self):
        # u = x^2 + y^2 satisfies ∇²u = 4
        nx, ny = 20, 20
        x = np.linspace(0, 1, nx)
        y = np.linspace(0, 1, ny)
        dx = x[1] - x[0]
        dy = y[1] - y[0]
        X, Y = np.meshgrid(x, y)
        u = X ** 2 + Y ** 2
        f = np.full_like(u, 4.0)  # Laplacian of x^2+y^2 = 4
        res = self.e.compute_pde_residual_poisson(u, f, dx, dy)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value, 0.0, atol=0.5)

    def test_boundary_loss(self):
        u_bc = np.array([0.0, 0.0, 0.0])
        target = np.array([0.0, 0.0, 0.0])
        res = self.e.boundary_loss_dirichlet(u_bc, target)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 0.0)


if __name__ == '__main__':
    unittest.main()
