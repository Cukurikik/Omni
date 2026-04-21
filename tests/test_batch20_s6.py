"""
Batch 20 Semester 6 — Integration Test Suite.
Validates all 7 engines across 11 repository knowledge domains.
"""
import unittest
import numpy as np

from src.compute.python_core.omni_img2dataset_engine import OmniImg2DatasetEngine
from src.compute.python_core.omni_tfprobability_engine import OmniTFProbabilityEngine
from src.compute.python_core.omni_alphazero_mcts_engine import OmniAlphaZeroMCTSEngine
from src.compute.python_core.omni_recbole_engine import OmniRecBoleEngine
from src.compute.python_core.omni_deepke_engine import OmniDeepKEEngine
from src.compute.python_core.omni_open_flamingo_engine import OmniOpenFlamingoEngine
from src.compute.python_core.omni_clearer_voice_engine import OmniClearerVoiceEngine


class TestImg2DatasetEngine(unittest.TestCase):
    """Tests for image dataset pipeline primitives."""

    def setUp(self):
        self.engine = OmniImg2DatasetEngine()

    def test_resize_nearest_2d(self):
        img = np.arange(100, dtype=np.float64).reshape(10, 10)
        res = self.engine.resize_nearest(img, 5, 5)
        self.assertIsInstance(res, type(res))
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (5, 5))

    def test_resize_nearest_3d(self):
        img = np.random.rand(8, 12, 3)
        res = self.engine.resize_nearest(img, 4, 6)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (4, 6, 3))

    def test_center_crop(self):
        img = np.ones((100, 100, 3), dtype=np.uint8)
        res = self.engine.center_crop(img, 50, 50)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (50, 50, 3))

    def test_center_crop_exceeds_bounds(self):
        img = np.ones((10, 10))
        res = self.engine.center_crop(img, 20, 20)
        self.assertEqual(res.__class__.__name__, "Err")

    def test_dhash_deterministic(self):
        img = np.random.RandomState(0).rand(64, 64, 3)
        h1 = self.engine.compute_dhash(img)
        h2 = self.engine.compute_dhash(img)
        self.assertEqual(h1.__class__.__name__, "Ok")
        np.testing.assert_array_equal(h1.value, h2.value)
        self.assertEqual(len(h1.value), 64)  # 8*8 bits

    def test_channel_stats(self):
        imgs = [np.full((4, 4, 3), fill_value=v, dtype=np.float64) for v in [0.2, 0.4, 0.6]]
        res = self.engine.compute_channel_stats(imgs)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value["mean"], [0.4, 0.4, 0.4], atol=1e-10)


class TestTFProbabilityEngine(unittest.TestCase):
    """Tests for probabilistic inference primitives."""

    def setUp(self):
        self.engine = OmniTFProbabilityEngine()

    def test_gaussian_log_prob(self):
        x = np.array([0.0])
        res = self.engine.gaussian_log_prob(x, mu=np.array([0.0]), sigma=np.array([1.0]))
        self.assertEqual(res.__class__.__name__, "Ok")
        expected = -0.5 * np.log(2 * np.pi)
        np.testing.assert_allclose(res.value, [expected], atol=1e-10)

    def test_gaussian_sample_shape(self):
        mu = np.array([0.0, 1.0])
        sigma = np.array([1.0, 0.5])
        res = self.engine.gaussian_sample(mu, sigma, n_samples=100)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (100, 2))

    def test_kl_divergence_self(self):
        mu = np.array([0.0, 1.0])
        sigma = np.array([1.0, 2.0])
        res = self.engine.kl_divergence_gaussian(mu, sigma, mu, sigma)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(res.value, 0.0, places=10)

    def test_bernoulli_log_prob(self):
        x = np.array([1.0, 0.0])
        probs = np.array([0.9, 0.1])
        res = self.engine.bernoulli_log_prob(x, probs)
        self.assertEqual(res.__class__.__name__, "Ok")
        np.testing.assert_allclose(res.value, [np.log(0.9), np.log(0.9)], atol=1e-10)

    def test_bayesian_posterior(self):
        data = np.array([5.0, 5.0, 5.0, 5.0, 5.0])
        res = self.engine.bayesian_posterior_normal(prior_mu=0.0, prior_sigma=10.0, data=data, likelihood_sigma=1.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        # Posterior should be pulled strongly toward data mean of 5.0
        self.assertGreater(res.value["posterior_mu"], 4.5)


class TestAlphaZeroMCTSEngine(unittest.TestCase):
    """Tests for AlphaZero MCTS primitives."""

    def setUp(self):
        self.engine = OmniAlphaZeroMCTSEngine(num_actions=4, c_puct=1.41)

    def test_ucb_selection(self):
        prior = np.array([0.25, 0.25, 0.25, 0.25])
        self.engine.get_or_create_node(state_hash=0, prior=prior)
        res = self.engine.select_action_ucb(0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertIn(res.value, [0, 1, 2, 3])

    def test_backpropagation(self):
        self.engine.get_or_create_node(state_hash=1)
        res = self.engine.backpropagate(1, action=2, value=1.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        node = self.engine.nodes[1]
        self.assertEqual(node.visit_count[2], 1.0)
        self.assertEqual(node.total_value[2], 1.0)

    def test_policy_extraction_greedy(self):
        self.engine.get_or_create_node(state_hash=2)
        self.engine.backpropagate(2, action=1, value=1.0)
        self.engine.backpropagate(2, action=1, value=1.0)
        self.engine.backpropagate(2, action=3, value=0.5)

        res = self.engine.extract_policy(2, temperature=0.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(np.argmax(res.value), 1)  # action 1 most visited
        self.assertAlmostEqual(res.value[1], 1.0)

    def test_policy_extraction_proportional(self):
        self.engine.get_or_create_node(state_hash=3)
        for _ in range(10):
            self.engine.backpropagate(3, action=0, value=1.0)
        for _ in range(5):
            self.engine.backpropagate(3, action=2, value=0.5)

        res = self.engine.extract_policy(3, temperature=1.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(np.sum(res.value), 1.0)
        self.assertGreater(res.value[0], res.value[2])


class TestRecBoleEngine(unittest.TestCase):
    """Tests for recommendation system primitives."""

    def setUp(self):
        self.engine = OmniRecBoleEngine()

    def test_cosine_similarity(self):
        matrix = np.array([[1, 0, 0], [0, 1, 0], [1, 0, 0]], dtype=np.float64)
        res = self.engine.cosine_similarity_matrix(matrix)
        self.assertEqual(res.__class__.__name__, "Ok")
        sim = res.value
        self.assertAlmostEqual(sim[0, 2], 1.0)  # identical vectors
        self.assertAlmostEqual(sim[0, 1], 0.0)  # orthogonal vectors

    def test_top_k_items(self):
        scores = np.array([0.1, 0.9, 0.5, 0.3, 0.8])
        res = self.engine.top_k_items(scores, k=3)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(list(res.value), [1, 4, 2])  # scores: 0.9, 0.8, 0.5

    def test_top_k_with_exclusion(self):
        scores = np.array([0.1, 0.9, 0.5, 0.3, 0.8])
        res = self.engine.top_k_items(scores, k=2, exclude_indices=np.array([1]))
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertNotIn(1, res.value)  # index 1 excluded

    def test_svd_factorization(self):
        R = np.array([[5, 3, 0, 1], [4, 0, 0, 1], [1, 1, 0, 5], [0, 0, 5, 4]], dtype=np.float64)
        res = self.engine.matrix_factorize_svd(R, n_factors=2)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["user_factors"].shape, (4, 2))
        self.assertEqual(res.value["item_factors"].shape, (4, 2))

    def test_predict_ratings(self):
        uf = np.array([[1, 0], [0, 1]], dtype=np.float64)
        itf = np.array([[1, 0], [0, 1], [1, 1]], dtype=np.float64)
        res = self.engine.predict_ratings(uf, itf)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (2, 3))


class TestDeepKEEngine(unittest.TestCase):
    """Tests for knowledge extraction primitives."""

    def setUp(self):
        self.engine = OmniDeepKEEngine()

    def test_bio_decoding(self):
        logits = np.array([[0.1, 0.9, 0.0], [0.0, 0.1, 0.9], [0.8, 0.1, 0.1]])
        label_map = {0: "O", 1: "B-PER", 2: "I-PER"}
        res = self.engine.decode_bio_tags(logits, label_map)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value, ["B-PER", "I-PER", "O"])

    def test_entity_span_extraction(self):
        tags = ["O", "B-PER", "I-PER", "O", "B-LOC", "O"]
        res = self.engine.extract_entity_spans(tags)
        self.assertEqual(res.__class__.__name__, "Ok")
        spans = res.value
        self.assertEqual(len(spans), 2)
        self.assertEqual(spans[0], ("PER", 1, 2))
        self.assertEqual(spans[1], ("LOC", 4, 4))

    def test_relation_classification(self):
        dim = 4
        entity_a = np.array([1, 0, 0, 0], dtype=np.float64)
        entity_b = np.array([0, 1, 0, 0], dtype=np.float64)
        rel_matrices = np.zeros((3, dim, dim), dtype=np.float64)
        rel_matrices[2, 0, 1] = 10.0  # Strong signal for relation 2

        res = self.engine.classify_relation(entity_a, entity_b, rel_matrices)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["best_relation"], 2)

    def test_int8_quantization(self):
        weights = np.array([[1.0, -0.5], [0.25, -1.0]])
        res = self.engine.quantize_weights_int8(weights)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value["quantized"].dtype, np.int8)
        self.assertGreater(res.value["scale"], 0)


class TestOpenFlamingoEngine(unittest.TestCase):
    """Tests for multimodal cross-attention primitives."""

    def setUp(self):
        self.engine = OmniOpenFlamingoEngine()

    def test_cross_attention_shapes(self):
        q = np.random.rand(5, 16)  # 5 language tokens
        k = np.random.rand(10, 16)  # 10 vision tokens
        v = np.random.rand(10, 16)
        res = self.engine.cross_attention(q, k, v)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (5, 16))

    def test_gated_cross_attention_gate_zero(self):
        lang = np.ones((3, 8))
        vis = np.random.rand(6, 8)
        res = self.engine.gated_cross_attention(lang, vis, gate_value=0.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        # Gate=0 → tanh(0)=0 → output == language_hidden
        np.testing.assert_array_almost_equal(res.value, lang)

    def test_perceiver_resample(self):
        vis_tokens = np.random.rand(20, 32)
        res = self.engine.perceiver_resample(vis_tokens, num_latents=4)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(res.value.shape, (4, 32))


class TestClearerVoiceEngine(unittest.TestCase):
    """Tests for audio enhancement primitives."""

    def setUp(self):
        self.engine = OmniClearerVoiceEngine(n_fft=256, hop_length=64)

    def test_stft_istft_roundtrip(self):
        original = np.random.rand(2048)
        stft_res = self.engine.stft(original)
        self.assertEqual(stft_res.__class__.__name__, "Ok")

        istft_res = self.engine.istft(stft_res.value, output_length=len(original))
        self.assertEqual(istft_res.__class__.__name__, "Ok")
        # Trim boundary samples where Hann window fade-in/out causes expected attenuation
        trim = self.engine.hop_length
        np.testing.assert_allclose(istft_res.value[trim:-trim], original[trim:-trim], atol=1e-6)

    def test_spectral_gate(self):
        clean = np.sin(2 * np.pi * 440 * np.linspace(0, 0.5, 8000))
        noise = np.random.RandomState(0).randn(8000) * 0.01
        noisy = clean + noise
        noise_sample = np.random.RandomState(0).randn(2000) * 0.01

        res = self.engine.spectral_gate(noisy, noise_sample, threshold_db=-10.0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(len(res.value), len(noisy))

    def test_wiener_filter(self):
        clean = np.sin(2 * np.pi * 220 * np.linspace(0, 0.5, 8000))
        noise = np.random.RandomState(1).randn(8000) * 0.05
        noisy = clean + noise
        noise_sample = np.random.RandomState(1).randn(2000) * 0.05

        res = self.engine.wiener_filter(noisy, noise_sample)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertEqual(len(res.value), len(noisy))


if __name__ == '__main__':
    unittest.main()
