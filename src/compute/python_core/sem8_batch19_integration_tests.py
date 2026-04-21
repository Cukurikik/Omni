"""
Semester 8 Batch 19 — Integration Tests
=======================================
Validates all 5 Batch 19 engines:
  1. OmniAlgoWikiEngine
  2. OmniCMLEngine
  3. OmniBinduEngine
  4. OmniBRAGEngine
  5. OmniLLMRLEngine
"""

import unittest
import numpy as np

from omni_algowiki_engine import OmniAlgoWikiEngine
from omni_cml_engine import OmniCMLEngine
from omni_bindu_engine import OmniBinduEngine
from omni_brag_engine import OmniBRAGEngine
from omni_llmrl_engine import OmniLLMRLEngine

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

class TestAlgoWikiEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniAlgoWikiEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_dijkstra_resolution(self):
        engine = OmniAlgoWikiEngine()
        # 0 - 1 - 2
        #  \     /
        #   \   /
        #     3
        # 0->1=1, 1->2=2 (Path A = 3)
        # 0->3=5, 3->2=1 (Path B = 6)
        graph = engine.init_graph(size=4)
        self.assertTrue(is_ok(graph.add_edge(0, 1, 1.0)))
        self.assertTrue(is_ok(graph.add_edge(1, 2, 2.0)))
        self.assertTrue(is_ok(graph.add_edge(0, 3, 5.0)))
        self.assertTrue(is_ok(graph.add_edge(3, 2, 1.0)))
        
        res = graph.shortest_path(origin=0)
        self.assertTrue(is_ok(res))
        distances = unwrap(res)
        
        self.assertEqual(distances[0], 0.0)
        self.assertEqual(distances[1], 1.0)
        self.assertEqual(distances[2], 3.0) # via node 1
        self.assertEqual(distances[3], 4.0) # via node 1 -> 2 -> 3


class TestCMLEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniCMLEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_metrics_differential(self):
        engine = OmniCMLEngine()
        validator = engine.configure_validator(strictness=0.10) # 10% bounds
        
        base_metrics = {"loss": 0.50, "accuracy": 0.90}
        
        # Test 1: Acceptable variation
        new_metrics_good = {"loss": 0.48, "accuracy": 0.92, "f1": 0.9}
        res_good = validator.assess_metrics(base_metrics, new_metrics_good)
        self.assertTrue(is_ok(res_good))
        self.assertTrue(unwrap(res_good)["approved"])
        
        # Test 2: Unacceptable regression
        new_metrics_bad = {"loss": 0.90, "accuracy": 0.88} # loss increased by 80%
        res_bad = validator.assess_metrics(base_metrics, new_metrics_bad)
        self.assertTrue(is_ok(res_bad))
        self.assertFalse(unwrap(res_bad)["approved"])


class TestBinduEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniBinduEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_ngram_tokenization(self):
        engine = OmniBinduEngine()
        vectorizer = engine.get_vectorizer(capacity=10)
        
        corpus = [
            "Hello world, this is bindu representation.",
            "Hello again, world."
        ]
        
        self.assertTrue(is_ok(vectorizer.fit(corpus)))
        
        res_trans = vectorizer.transform(corpus)
        self.assertTrue(is_ok(res_trans))
        matrix = unwrap(res_trans)
        
        self.assertEqual(matrix.shape, (2, len(vectorizer._vocab_idx)))
        # 'hello' and 'world' should have occurrences in both docs
        hello_idx = vectorizer._vocab_idx.get("hello")
        self.assertIsNotNone(hello_idx)
        self.assertEqual(matrix[0, hello_idx], 1.0)
        self.assertEqual(matrix[1, hello_idx], 1.0)


class TestBRAGEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniBRAGEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_bm25_retrieval(self):
        engine = OmniBRAGEngine()
        bm25 = engine.get_bm25_system()
        
        corpus = [
            "The quick brown fox jumps over the lazy dog.",
            "Artificial Intelligence is transforming the digital world.",
            "The lazy dog sleeps all day without a single jump."
        ]
        
        self.assertTrue(is_ok(bm25.add_corpus(corpus)))
        
        # Query matching document 2 highly
        res = bm25.query_rank("lazy dog sleeps", top_k=2)
        self.assertTrue(is_ok(res))
        
        rankings = unwrap(res)
        self.assertEqual(len(rankings), 2)
        # Should place document index 2 as highest
        self.assertEqual(rankings[0]["id"], 2)


class TestLLMRLEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniLLMRLEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_ppo_advantages(self):
        engine = OmniLLMRLEngine()
        ppo = engine.get_ppo_estimator(gamma=0.9, lam=0.9)
        
        # Simulated sequence trajectory
        rewards = np.array([1.0, 0.5, 0.0, -1.0])
        values = np.array([0.8, 0.6, 0.2, 0.0]) # Critic predictions
        
        res_gae = ppo.estimate_advantages(rewards, values, next_value=0.0)
        self.assertTrue(is_ok(res_gae))
        advantages = unwrap(res_gae)
        
        self.assertEqual(advantages.shape, (4,))
        # Last step advantage calculation:
        # delta = reward + gamma * next_val - current_val = -1.0 + 0 - 0.0 = -1.0
        # gae = -1.0
        self.assertEqual(advantages[3], -1.0)
        
        # Let's perform a dummy surrogate loss check
        old_probs = np.array([0.5, 0.5, 0.5, 0.5])
        new_probs = np.array([0.6, 0.4, 0.6, 0.4])
        res_loss = ppo.ppo_clip_loss(old_probs, new_probs, advantages, epsilon=0.2)
        self.assertTrue(is_ok(res_loss))
        
        
if __name__ == "__main__":
    unittest.main()
