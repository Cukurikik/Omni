"""
Batch 25 Semester 6 — Integration Test Suite.

Validates all 5 NEW engines:
  1. OmniHuggingFaceNLPEngine    (huggingface/course)
  2. OmniMMPretrainEngine        (open-mmlab/mmpretrain)
  3. OmniSwanLabEngine           (SwanHubX/SwanLab)
  4. OmniLazyLLMEngine           (LazyAGI/LazyLLM)
  5. OmniScenicEngine            (google-research/scenic)

Tests: 50 | Zero-algebraic_bound | Pure NumPy
"""
import unittest
import math
import json
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.compute.python_core.omni_huggingface_nlp_engine import OmniHuggingFaceNLPEngine
from src.compute.python_core.omni_mmpretrain_engine import OmniMMPretrainEngine
from src.compute.python_core.omni_swanlab_engine import OmniSwanLabEngine
from src.compute.python_core.omni_lazyllm_engine import OmniLazyLLMEngine
from src.compute.python_core.omni_scenic_engine import OmniScenicEngine


# =========================================================================
#  1. HUGGINGFACE NLP ENGINE — 10 tests
# =========================================================================

class TestHuggingFaceNLPEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniHuggingFaceNLPEngine()
        corpus = ["the cat sat on the mat", "the dog ran in the park", "a bird flew over"]
        self.vocab_res = self.e.build_vocab(corpus)
        self.token2id = self.vocab_res.value["token2id"]

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_build_vocab(self):
        self.assertIn("[PAD]", self.token2id)
        self.assertIn("[UNK]", self.token2id)
        self.assertIn("the", self.token2id)

    def test_tokenize_words(self):
        res = self.e.tokenize_words("The Cat Sat")
        self.assertEqual(res.value, ["the", "cat", "sat"])

    def test_encode(self):
        tokens = ["the", "cat", "sat"]
        res = self.e.encode(tokens, self.token2id, max_length=8)
        self.assertEqual(len(res.value["input_ids"]), 8)
        self.assertEqual(res.value["attention_mask"][-1], 0)  # padded

    def test_classify(self):
        logits = np.array([0.1, 2.0, 0.5])
        res = self.e.classify(logits, ["neg", "pos", "neutral"])
        self.assertEqual(res.value["label"], "pos")
        self.assertGreater(res.value["score"], 0.5)

    def test_ner_decode(self):
        logits = np.array([
            [3.0, 0.1, 0.1],  # O
            [0.1, 3.0, 0.1],  # B-PER
            [0.1, 0.1, 3.0],  # I-PER
            [3.0, 0.1, 0.1],  # O
        ])
        tokens = ["hello", "john", "smith", "today"]
        tags = ["O", "B-PER", "I-PER"]
        res = self.e.ner_decode(logits, tokens, tags)
        self.assertEqual(len(res.value), 1)
        self.assertEqual(res.value[0]["entity"], "PER")
        self.assertEqual(res.value[0]["tokens"], ["john", "smith"])

    def test_qa_extract(self):
        start = np.array([0.1, 0.2, 3.0, 0.1, 0.1])
        end = np.array([0.1, 0.1, 0.1, 0.1, 3.0])
        tokens = ["the", "answer", "is", "forty", "two"]
        res = self.e.qa_extract(start, end, tokens, n_best=3)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(len(res.value), 0)

    def test_generate_greedy(self):
        logits = np.array([[0.1, 3.0, 0.2], [2.0, 0.1, 0.3], [0.1, 0.2, 5.0]])
        res = self.e.generate_greedy(logits)
        self.assertEqual(res.value, [1, 0, 2])

    def test_generate_topk(self):
        logits = np.random.RandomState(0).randn(100)
        res = self.e.generate_topk(logits, k=5, seed=42)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertIn(res.value, range(100))

    def test_perplexity(self):
        log_probs = np.log(np.array([0.5, 0.3, 0.8, 0.4]))
        res = self.e.perplexity(log_probs)
        self.assertGreater(res.value, 1.0)


# =========================================================================
#  2. MMPRETRAIN ENGINE — 10 tests
# =========================================================================

class TestMMPretrainEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniMMPretrainEngine()
        self.img = np.random.RandomState(0).rand(32, 32, 3)

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_random_crop(self):
        res = self.e.random_crop(self.img, 16, 16)
        self.assertEqual(res.value.shape, (16, 16, 3))

    def test_random_flip(self):
        res = self.e.random_flip(self.img, seed=0)
        self.assertEqual(res.value.shape, self.img.shape)

    def test_color_jitter(self):
        res = self.e.color_jitter(self.img, seed=0)
        self.assertEqual(res.value.shape, self.img.shape)
        self.assertTrue(np.all(res.value >= 0) and np.all(res.value <= 1))

    def test_cutout(self):
        res = self.e.cutout(self.img, n_holes=2, hole_size=8, seed=0)
        self.assertEqual(res.value.shape, self.img.shape)

    def test_mixup(self):
        x1 = np.ones((8, 8, 3))
        x2 = np.zeros((8, 8, 3))
        y1 = np.array([1.0, 0.0])
        y2 = np.array([0.0, 1.0])
        res = self.e.mixup(x1, y1, x2, y2, alpha=0.2, seed=0)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertAlmostEqual(np.sum(res.value["label"]), 1.0)

    def test_cutmix(self):
        x1 = np.ones((16, 16, 3))
        x2 = np.zeros((16, 16, 3))
        y1 = np.array([1.0, 0.0])
        y2 = np.array([0.0, 1.0])
        res = self.e.cutmix(x1, y1, x2, y2, seed=0)
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_se_attention(self):
        feat = np.random.RandomState(0).randn(8, 4, 4)
        W_down = np.random.RandomState(1).randn(2, 8) * 0.1
        W_up = np.random.RandomState(2).randn(8, 2) * 0.1
        res = self.e.se_attention(feat, W_down, W_up)
        self.assertEqual(res.value.shape, (8, 4, 4))

    def test_topk_accuracy(self):
        logits = np.array([[0.1, 0.9, 0.0], [0.8, 0.1, 0.1], [0.0, 0.0, 1.0]])
        targets = np.array([1, 0, 2])
        res = self.e.topk_accuracy(logits, targets, k=1)
        self.assertAlmostEqual(res.value, 1.0)

    def test_contrastive_loss(self):
        z_i = np.random.RandomState(0).randn(4, 8)
        z_j = np.random.RandomState(1).randn(4, 8)
        res = self.e.contrastive_loss(z_i, z_j, temperature=0.5)
        self.assertEqual(res.__class__.__name__, "Ok")
        self.assertGreater(res.value, 0)


# =========================================================================
#  3. SWANLAB ENGINE — 10 tests
# =========================================================================

class TestSwanLabEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniSwanLabEngine()
        self.e.init_run("run1", {"lr": 0.01, "batch_size": 32}, tags=["test"])

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_init_run(self):
        res = self.e.init_run("run2", {"lr": 0.001})
        self.assertEqual(res.value, "run2")
        # Duplicate should fail
        res2 = self.e.init_run("run2", {})
        self.assertEqual(res2.__class__.__name__, "Err")

    def test_log_scalar(self):
        res = self.e.log_scalar("loss", 0.5, step=1)
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_log_scalars(self):
        res = self.e.log_scalars({"loss": 0.3, "acc": 0.8}, step=2)
        self.assertEqual(res.value["logged"], 2)

    def test_log_histogram(self):
        vals = np.random.RandomState(0).randn(100)
        res = self.e.log_histogram("weights", vals, step=1)
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_get_metric_history(self):
        self.e.log_scalar("loss", 0.5, step=1)
        self.e.log_scalar("loss", 0.3, step=2)
        res = self.e.get_metric_history("loss")
        self.assertEqual(len(res.value), 2)

    def test_get_summary(self):
        for i in range(5):
            self.e.log_scalar("loss", 1.0 - i * 0.1, step=i)
        res = self.e.get_summary("loss")
        self.assertAlmostEqual(res.value["last"], 0.6)

    def test_compare_runs(self):
        self.e.init_run("cmp_a", {"lr": 0.01})
        self.e.log_scalar("loss", 0.5, step=1, run_id="cmp_a")
        self.e.init_run("cmp_b", {"lr": 0.001})
        self.e.log_scalar("loss", 0.3, step=1, run_id="cmp_b")
        res = self.e.compare_runs(["cmp_a", "cmp_b"], "loss")
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_hp_grid(self):
        res = self.e.hp_grid({"lr": [0.01, 0.001], "bs": [16, 32]})
        self.assertEqual(len(res.value), 4)

    def test_finish_run(self):
        res = self.e.finish_run("run1")
        self.assertEqual(res.value["status"], "finished")


# =========================================================================
#  4. LAZYLLM ENGINE — 10 tests
# =========================================================================

class TestLazyLLMEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniLazyLLMEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_render_prompt(self):
        res = self.e.render_prompt("Hello {name}, welcome to {place}!", {"name": "Tuan", "place": "OMNI"})
        self.assertEqual(res.value, "Hello Tuan, welcome to OMNI!")

    def test_render_prompt_unresolved(self):
        res = self.e.render_prompt("Hello {name}!", {})
        self.assertEqual(res.__class__.__name__, "Err")

    def test_chain_of_thought(self):
        res = self.e.chain_of_thought("What is 2+2?", ["Add 2 and 2", "Result is 4"])
        self.assertIn("Step 1", res.value)
        self.assertIn("Step 2", res.value)

    def test_tool_schema(self):
        res = self.e.tool_schema(
            "get_weather", "Get current weather",
            {"city": {"type": "string", "description": "City name"}}
        )
        self.assertEqual(res.value["function"]["name"], "get_weather")

    def test_parse_tool_call(self):
        text = 'Sure! ```json\n{"action": "search", "query": "test"}\n```'
        res = self.e.parse_tool_call(text)
        self.assertEqual(res.value["action"], "search")

    def test_sequential_pipeline(self):
        steps = [lambda x: x + 1, lambda x: x * 2, lambda x: x - 3]
        res = self.e.sequential_pipeline(5, steps)
        self.assertEqual(res.value, 9)  # (5+1)*2-3 = 9

    def test_route(self):
        routes = {"weather": ["weather", "temperature"], "news": ["news", "headline"]}
        res = self.e.route("What's the weather today?", routes)
        self.assertEqual(res.value, "weather")

    def test_rag_retrieve(self):
        q = np.array([1.0, 0.0, 0.0])
        docs = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.5, 0.5, 0.0]])
        texts = ["doc_a", "doc_b", "doc_c"]
        res = self.e.rag_retrieve(q, docs, texts, top_k=2)
        self.assertEqual(res.value[0][0], "doc_a")

    def test_sliding_window(self):
        history = [{"role": "user", "content": f"msg{i}"} for i in range(10)]
        res = self.e.sliding_window_memory(history, 3)
        self.assertEqual(len(res.value), 3)


# =========================================================================
#  5. SCENIC ENGINE — 10 tests
# =========================================================================

class TestScenicEngine(unittest.TestCase):

    def setUp(self):
        self.e = OmniScenicEngine()

    def test_diagnostics(self):
        res = self.e.diagnostics()
        self.assertEqual(res.__class__.__name__, "Ok")

    def test_patch_embed(self):
        img = np.random.RandomState(0).randn(16, 16, 3)
        P = 4
        D = 32
        W_proj = np.random.RandomState(1).randn(P * P * 3, D) * 0.1
        res = self.e.patch_embed(img, P, W_proj)
        self.assertEqual(res.value.shape, (16, D))  # 16 patches = 4x4 grid

    def test_sinusoidal_pos_2d(self):
        res = self.e.sinusoidal_pos_enc_2d(4, 4, 32)
        self.assertEqual(res.value.shape, (16, 32))

    def test_layer_norm(self):
        x = np.random.RandomState(0).randn(8, 16)
        gamma = np.ones(16)
        beta = np.zeros(16)
        res = self.e.layer_norm(x, gamma, beta)
        # Should be ~zero mean per row
        means = np.mean(res.value, axis=-1)
        np.testing.assert_allclose(means, 0, atol=1e-5)

    def test_mhsa(self):
        D = 16
        N = 8
        x = np.random.RandomState(0).randn(N, D)
        Wq = np.random.RandomState(1).randn(D, D) * 0.1
        Wk = np.random.RandomState(2).randn(D, D) * 0.1
        Wv = np.random.RandomState(3).randn(D, D) * 0.1
        Wo = np.random.RandomState(4).randn(D, D) * 0.1
        res = self.e.multi_head_self_attention(x, Wq, Wk, Wv, Wo, n_heads=4)
        self.assertEqual(res.value.shape, (N, D))

    def test_mlp_block(self):
        D = 8
        D_ff = 32
        x = np.random.RandomState(0).randn(4, D)
        W1 = np.random.RandomState(1).randn(D, D_ff) * 0.1
        b1 = np.zeros(D_ff)
        W2 = np.random.RandomState(2).randn(D_ff, D) * 0.1
        b2 = np.zeros(D)
        res = self.e.mlp_block(x, W1, b1, W2, b2)
        self.assertEqual(res.value.shape, (4, D))

    def test_vit_block(self):
        D = 16
        D_ff = 32
        N = 8
        rng = np.random.RandomState(0)
        x = rng.randn(N, D)
        g1 = np.ones(D); b1 = np.zeros(D)
        Wq = rng.randn(D, D) * 0.02; Wk = rng.randn(D, D) * 0.02
        Wv = rng.randn(D, D) * 0.02; Wo = rng.randn(D, D) * 0.02
        g2 = np.ones(D); b2 = np.zeros(D)
        W_ff1 = rng.randn(D, D_ff) * 0.02; b_ff1 = np.zeros(D_ff)
        W_ff2 = rng.randn(D_ff, D) * 0.02; b_ff2 = np.zeros(D)
        res = self.e.vit_block(x, g1, b1, Wq, Wk, Wv, Wo, 4, g2, b2, W_ff1, b_ff1, W_ff2, b_ff2)
        self.assertEqual(res.value.shape, (N, D))

    def test_cls_pool(self):
        tokens = np.random.RandomState(0).randn(10, 16)
        res = self.e.cls_pool(tokens)
        np.testing.assert_array_equal(res.value, tokens[0])

    def test_image_normalize(self):
        img = np.random.RandomState(0).rand(8, 8, 3) * 255
        mean = np.array([123.675, 116.28, 103.53])
        std = np.array([58.395, 57.12, 57.375])
        res = self.e.image_normalize(img, mean, std)
        self.assertEqual(res.value.shape, (8, 8, 3))

    def test_feature_pyramid(self):
        fmaps = [np.random.randn(16, 8, 8), np.random.randn(32, 4, 4), np.random.randn(64, 2, 2)]
        res = self.e.feature_pyramid(fmaps)
        self.assertEqual(len(res.value), 3)
        self.assertEqual(res.value[0].shape, (16,))
        self.assertEqual(res.value[2].shape, (64,))


if __name__ == '__main__':
    unittest.main()
