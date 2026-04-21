"""
Batch 23 Semester 6 — Integration Test Suite.

Validates all 6 NEW engines:
  1. OmniSuperGlueEngine     (magicleap/SuperGluePretrainedNetwork)
  2. OmniDARTSEngine          (quark0/darts)
  3. OmniDeepTextRecogEngine  (clovaai/deep-text-recognition-benchmark)
  4. OmniFSRSEngine           (open-spaced-repetition/fsrs4anki)
  5. OmniTransferLearningEngine (thuml/Transfer-Learning-Library)
  6. OmniSatelliteImageryEngine (chrieke/awesome-satellite-imagery-datasets)

Tests: ~60 | Zero-mock | Pure NumPy
"""
import unittest
import math
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.compute.python_core.omni_superglue_engine import OmniSuperGlueEngine
from src.compute.python_core.omni_darts_engine import OmniDARTSEngine
from src.compute.python_core.omni_deep_text_recog_engine import OmniDeepTextRecogEngine
from src.compute.python_core.omni_fsrs_engine import OmniFSRSEngine, CardState, AGAIN, HARD, GOOD, EASY
from src.compute.python_core.omni_transfer_learning_engine import OmniTransferLearningEngine
from src.compute.python_core.omni_satellite_imagery_engine import OmniSatelliteImageryEngine


# =========================================================================
#  1. SUPERGLUE ENGINE — 10 tests
# =========================================================================

class TestSuperGlueEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniSuperGlueEngine(descriptor_dim=32)

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_encode_keypoints(self):
        kp = np.array([[0.1, 0.2], [0.5, 0.6], [0.9, 0.8]])
        scores = np.array([0.9, 0.8, 0.7])
        W = np.random.RandomState(0).randn(32, 2) * 0.1
        b = np.zeros(32)
        res = self.e.encode_keypoints(kp, scores, W, b)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (3, 32))

    def test_fuse_descriptors(self):
        d1 = np.ones((3, 32))
        d2 = np.ones((3, 32)) * 2
        res = self.e.fuse_descriptors(d1, d2)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value, 3.0)

    def test_self_attention(self):
        feat = np.random.RandomState(0).randn(5, 32)
        W = np.eye(32) * 0.1
        res = self.e.self_attention_layer(feat, W, W, W)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (5, 32))

    def test_cross_attention(self):
        fa = np.random.RandomState(0).randn(4, 32)
        fb = np.random.RandomState(1).randn(6, 32)
        W = np.eye(32) * 0.1
        res = self.e.cross_attention_layer(fa, fb, W, W, W)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (4, 32))

    def test_sinkhorn(self):
        scores = np.random.RandomState(0).randn(4, 5)
        res = self.e.sinkhorn(scores, iterations=10)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (5, 6))  # augmented

    def test_mutual_nn(self):
        rng = np.random.RandomState(0)
        desc_a = rng.randn(5, 32)
        desc_b = desc_a[[3, 1, 4, 0, 2]] + rng.randn(5, 32) * 0.01
        res = self.e.mutual_nearest_neighbors(desc_a, desc_b)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(len(res.value["matches"]), 0)

    def test_dual_softmax(self):
        rng = np.random.RandomState(0)
        da = rng.randn(4, 32)
        da /= np.linalg.norm(da, axis=1, keepdims=True)
        db = rng.randn(5, 32)
        db /= np.linalg.norm(db, axis=1, keepdims=True)
        res = self.e.dual_softmax_match(da, db)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (4, 5))

    def test_filter_matches(self):
        matches = np.array([[0, 1], [1, 2], [2, 3]])
        confs = np.array([0.9, 0.3, 0.8])
        res = self.e.filter_matches(matches, confs, threshold=0.5)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(len(res.value["matches"]), 2)

    def test_lowe_ratio_test(self):
        rng = np.random.RandomState(42)
        da = rng.randn(3, 16)
        db = np.vstack([da + rng.randn(3, 16) * 0.01, rng.randn(5, 16)])
        res = self.e.lowe_ratio_test(da, db, ratio=0.8)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(len(res.value["matches"]), 0)


# =========================================================================
#  2. DARTS ENGINE — 10 tests
# =========================================================================

class TestDARTSEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniDARTSEngine(n_ops=8, n_nodes=4)

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["n_ops"], 8)

    def test_init_alphas(self):
        res = self.e.init_alphas(seed=0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["alpha_normal"].shape[1], 8)
        self.assertEqual(res.value["alpha_reduce"].shape[1], 8)

    def test_softmax_weights(self):
        alphas = np.random.RandomState(0).randn(14, 8)
        res = self.e.softmax_weights(alphas)
        self.assertEqual(res.__class__.__name__, "Ok")
        row_sums = np.sum(res.value, axis=1)
        np.testing.assert_allclose(row_sums, 1.0, atol=1e-6)

    def test_gumbel_softmax(self):
        alphas = np.random.RandomState(0).randn(14, 8)
        res = self.e.gumbel_softmax(alphas, temperature=0.5, seed=42)
        self.assertEqual(res.__class__.__name__, "Ok")
        row_sums = np.sum(res.value, axis=1)
        np.testing.assert_allclose(row_sums, 1.0, atol=1e-6)

    def test_mixed_operation(self):
        inputs = [np.ones(10) * i for i in range(8)]
        weights = np.array([0, 0, 0, 0, 0.5, 0.5, 0, 0])
        res = self.e.mixed_operation(inputs, weights)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value, 4.5)

    def test_op_zero(self):
        x = np.random.randn(10)
        res = self.e.op_zero(x)
        np.testing.assert_allclose(res.value, 0.0)

    def test_op_identity(self):
        x = np.random.randn(10)
        res = self.e.op_identity(x)
        np.testing.assert_allclose(res.value, x)

    def test_extract_genotype(self):
        alphas = np.random.RandomState(0).randn(14, 8)
        res = self.e.extract_genotype(alphas)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(len(res.value), 8)  # 4 nodes * 2 edges

    def test_cross_entropy_loss(self):
        logits = np.array([[2.0, 0.5, 0.1], [0.1, 3.0, 0.2]])
        targets = np.array([0, 1])
        res = self.e.compute_cross_entropy_loss(logits, targets)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertLess(res.value, 1.0)

    def test_architecture_entropy(self):
        # Uniform alphas → max entropy
        alphas_uniform = np.zeros((14, 8))
        res_u = self.e.architecture_entropy(alphas_uniform)
        # One-hot alphas → zero entropy
        alphas_onehot = np.full((14, 8), -100.0)
        alphas_onehot[:, 0] = 100.0
        res_o = self.e.architecture_entropy(alphas_onehot)
        self.assertGreater(res_u.value, res_o.value)


# =========================================================================
#  3. DEEP TEXT RECOGNITION ENGINE — 10 tests
# =========================================================================

class TestDeepTextRecogEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniDeepTextRecogEngine(n_classes=37)

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_tps_grid(self):
        ctrl = np.array([[0.0, 0.0], [0.5, 0.0], [1.0, 0.0],
                         [0.0, 1.0], [0.5, 1.0], [1.0, 1.0]])
        tgt = ctrl.copy()  # identity transform
        res = self.e.tps_grid(ctrl, tgt, grid_size=(4, 8))
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (32, 2))

    def test_cnn_feature_extract(self):
        img = np.random.RandomState(0).randn(100)
        W1 = np.random.RandomState(1).randn(64, 100) * 0.1
        b1 = np.zeros(64)
        W2 = np.random.RandomState(2).randn(32, 64) * 0.1
        b2 = np.zeros(32)
        res = self.e.cnn_feature_extract(img, W1, b1, W2, b2)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (32,))

    def test_sequential_features(self):
        feat = np.random.randn(20)
        res = self.e.sequential_features(feat, seq_len=5)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (5, 4))

    def test_lstm_cell(self):
        input_dim, hidden_dim = 4, 8
        x = np.random.RandomState(0).randn(input_dim)
        h = np.zeros(hidden_dim)
        c = np.zeros(hidden_dim)
        W = np.random.RandomState(1).randn(4 * hidden_dim, input_dim) * 0.1
        U = np.random.RandomState(2).randn(4 * hidden_dim, hidden_dim) * 0.1
        b = np.zeros(4 * hidden_dim)
        res = self.e.lstm_cell(x, h, c, W, U, b)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["h_new"].shape, (8,))

    def test_bilstm(self):
        seq = np.random.RandomState(0).randn(5, 4)
        hidden = 8
        W = np.random.RandomState(1).randn(4 * hidden, 4) * 0.1
        U = np.random.RandomState(2).randn(4 * hidden, hidden) * 0.1
        b = np.zeros(4 * hidden)
        res = self.e.bilstm(seq, W, U, b, W, U, b)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (5, 16))  # 2*hidden

    def test_ctc_greedy_decode(self):
        # Sequence: blank, A(1), A(1), blank, B(2) → [1, 2]
        log_probs = np.log(np.array([
            [0.9, 0.05, 0.05],
            [0.1, 0.8, 0.1],
            [0.1, 0.8, 0.1],
            [0.8, 0.1, 0.1],
            [0.1, 0.1, 0.8],
        ]) + 1e-10)
        res = self.e.ctc_greedy_decode(log_probs, blank=0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value, [1, 2])

    def test_ctc_loss(self):
        T, C = 10, 5
        log_probs = np.log(np.ones((T, C)) / C)
        targets = [1, 2]
        res = self.e.ctc_loss(log_probs, targets, blank=0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value, 0)

    def test_labels_to_string(self):
        labels = [1, 8, 5, 12, 12, 15]  # 0→'0', 1→'1', ... map: 1→0, ...
        res = self.e.labels_to_string(labels)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(len(res.value), 6)

    def test_ctc_decode_empty(self):
        # All blank
        log_probs = np.log(np.array([[0.9, 0.05, 0.05]] * 5) + 1e-10)
        res = self.e.ctc_greedy_decode(log_probs, blank=0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value, [])


# =========================================================================
#  4. FSRS ENGINE — 10 tests
# =========================================================================

class TestFSRSEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniFSRSEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_retrievability_fresh(self):
        res = self.e.retrievability(0, 10.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 1.0)

    def test_retrievability_decay(self):
        res = self.e.retrievability(100, 10.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertLess(res.value, 0.5)

    def test_initial_stability(self):
        # Easy grade should give highest initial stability
        s_again = self.e.initial_stability(AGAIN).value
        s_easy = self.e.initial_stability(EASY).value
        self.assertGreater(s_easy, s_again)

    def test_initial_difficulty(self):
        d_again = self.e.initial_difficulty(AGAIN).value
        d_easy = self.e.initial_difficulty(EASY).value
        self.assertGreater(d_again, d_easy)

    def test_optimal_interval(self):
        res = self.e.optimal_interval(10.0, 0.9)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 10.0, places=0)

    def test_schedule_first_review(self):
        state = CardState()
        res = self.e.schedule_card(state, GOOD, 0.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value["interval"], 0)
        self.assertEqual(res.value["new_state"].reps, 1)

    def test_schedule_lapse(self):
        state = CardState(stability=10.0, difficulty=5.0, reps=5, last_review=0)
        res = self.e.schedule_card(state, AGAIN, 10.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertLess(res.value["stability"], 10.0)
        self.assertEqual(res.value["new_state"].lapses, 1)

    def test_simulate_reviews(self):
        grades = [GOOD, GOOD, GOOD, EASY, GOOD]
        res = self.e.simulate_reviews(grades)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(len(res.value), 5)
        # Stability should increase with successive GOOD grades
        stabilities = [r["stability"] for r in res.value]
        self.assertGreater(stabilities[-1], stabilities[0])

    def test_retention_curve(self):
        res = self.e.compute_retention_curve(10.0, max_days=30)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(len(res.value), 30)
        self.assertAlmostEqual(res.value[0], 1.0)
        self.assertLess(res.value[-1], 1.0)


# =========================================================================
#  5. TRANSFER LEARNING ENGINE — 10 tests
# =========================================================================

class TestTransferLearningEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniTransferLearningEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_mmd_linear_same(self):
        data = np.random.RandomState(0).randn(100, 10)
        res = self.e.mmd_linear(data, data)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 0.0, places=5)

    def test_mmd_linear_different(self):
        src = np.random.RandomState(0).randn(100, 10)
        tgt = np.random.RandomState(0).randn(100, 10) + 3
        res = self.e.mmd_linear(src, tgt)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value, 1.0)

    def test_mmd_rbf(self):
        src = np.random.RandomState(0).randn(50, 5)
        tgt = np.random.RandomState(1).randn(50, 5) + 2
        res = self.e.mmd_rbf(src, tgt, sigma=1.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value, 0)

    def test_coral(self):
        src = np.random.RandomState(0).randn(50, 5)
        tgt = np.random.RandomState(0).randn(50, 5) * 2
        res = self.e.coral(src, tgt)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value, 0)

    def test_a_distance(self):
        src = np.random.RandomState(0).randn(100, 5)
        tgt = np.random.RandomState(0).randn(100, 5) + 5
        res = self.e.a_distance(src, tgt)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value["a_distance"], 0)

    def test_domain_classifier_loss(self):
        logits = np.array([2.0, -1.0, 3.0, -2.0])
        labels = np.array([1.0, 0.0, 1.0, 0.0])
        res = self.e.domain_classifier_loss(logits, labels)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertLess(res.value, 1.0)

    def test_dann_lambda(self):
        res_0 = self.e.dann_lambda_schedule(0, 100)
        res_50 = self.e.dann_lambda_schedule(50, 100)
        res_100 = self.e.dann_lambda_schedule(100, 100)
        self.assertAlmostEqual(res_0.value, 0.0, places=1)
        self.assertGreater(res_50.value, 0.3)
        self.assertAlmostEqual(res_100.value, 1.0, places=1)

    def test_transferability_score(self):
        src = np.random.RandomState(0).randn(50, 5)
        tgt = src + np.random.RandomState(1).randn(50, 5) * 0.01
        res = self.e.transferability_score(src, tgt)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value, 0.5)

    def test_class_conditional_alignment(self):
        src = np.random.RandomState(0).randn(60, 5)
        tgt = np.random.RandomState(1).randn(60, 5)
        src_labels = np.array([0]*20 + [1]*20 + [2]*20)
        tgt_labels = np.array([0]*20 + [1]*20 + [2]*20)
        res = self.e.class_conditional_alignment(src, tgt, src_labels, tgt_labels)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertIn("per_class_mmd", res.value)


# =========================================================================
#  6. SATELLITE IMAGERY ENGINE — 10 tests
# =========================================================================

class TestSatelliteImageryEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniSatelliteImageryEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_band_statistics(self):
        raster = np.random.RandomState(0).rand(4, 32, 32)
        res = self.e.band_statistics(raster)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertIn(0, res.value)
        self.assertGreater(res.value[0]["std"], 0)

    def test_normalize_bands(self):
        raster = np.random.RandomState(0).rand(3, 10, 10) * 255
        means = np.array([100, 120, 130], dtype=np.float64)
        stds = np.array([50, 40, 60], dtype=np.float64)
        res = self.e.normalize_bands(raster, means, stds)
        self.assertEqual(res.__class__.__name__, "Ok")
        # Normalized values should be centered near 0
        self.assertAlmostEqual(np.mean(res.value), 0.0, delta=5)

    def test_histogram_equalize(self):
        band = np.random.RandomState(0).randint(0, 100, (20, 20))
        res = self.e.histogram_equalize(band)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (20, 20))

    def test_generate_chips(self):
        raster = np.random.RandomState(0).rand(3, 64, 64)
        res = self.e.generate_chips(raster, chip_size=16, stride=16)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["n_chips"], 16)  # 4x4 chips

    def test_filter_chips(self):
        chips = [
            {"chip": np.ones((3, 8, 8))},
            {"chip": np.zeros((3, 8, 8))},  # all nodata
        ]
        res = self.e.filter_chips_by_content(chips, min_valid_fraction=0.5, nodata_value=0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(len(res.value), 1)

    def test_rasterize_labels(self):
        label = np.array([[0, 1], [2, 0]])
        res = self.e.rasterize_labels(label, n_classes=3)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (3, 2, 2))
        self.assertEqual(res.value[1, 0, 1], 1.0)

    def test_class_weights(self):
        label = np.array([[0, 0, 0, 0], [0, 0, 0, 1]])
        res = self.e.compute_class_weights(label, n_classes=2)
        self.assertEqual(res.__class__.__name__, "Ok")
        # Class 1 is rare → higher weight
        self.assertGreater(res.value[1], res.value[0])

    def test_stratified_sample(self):
        labels = np.array([0]*50 + [1]*50)
        res = self.e.stratified_sample(labels, n_samples=20)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(len(res.value), 20)

    def test_iou_matrix(self):
        boxes_a = np.array([[0, 0, 10, 10], [20, 20, 30, 30]], dtype=np.float64)
        boxes_b = np.array([[5, 5, 15, 15], [20, 20, 30, 30]], dtype=np.float64)
        res = self.e.compute_iou_matrix(boxes_a, boxes_b)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (2, 2))
        # boxes_a[1] and boxes_b[1] should be perfect match
        self.assertAlmostEqual(res.value[1, 1], 1.0, places=2)
        # boxes_a[0] and boxes_b[0] partial overlap
        self.assertGreater(res.value[0, 0], 0)
        self.assertLess(res.value[0, 0], 1.0)


if __name__ == '__main__':
    unittest.main()
