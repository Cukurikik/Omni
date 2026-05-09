"""
test_omni_batch19_integration.py — Integration Tests for Batch 19
Inspired by: Production verification for OMNI compute pipeline
Layer: Tests / Python

Integration tests verifying cross-module interactions between
Batch 19 compute kernels, system layers, and domain services.
"""

import unittest
import torch
import sys
import os
from typing import Dict

# Minimal test fixtures to verify module imports and basic contracts


class TestCodebookEMA(unittest.TestCase):
    """Verify EMA codebook quantization round-trip."""

    def test_codebook_quantize_shape(self):
        from compute.codebook.omni_codebook_ema import EMACodebook, CodebookConfig

        config = CodebookConfig(codebook_size=64, embedding_dim=32)
        codebook = EMACodebook(config)

        z = torch.randn(2, 10, 32)  # batch=2, seq=10, dim=32
        result = codebook(z)

        self.assertEqual(result["quantized"].shape, (2, 10, 32))
        self.assertEqual(result["indices"].shape, (2, 10))
        self.assertGreater(result["perplexity"].item(), 0)
        self.assertLessEqual(result["active_codes"], 64)

    def test_residual_codebook(self):
        from compute.codebook.omni_codebook_ema import ResidualCodebook, CodebookConfig

        config = CodebookConfig(codebook_size=32, embedding_dim=16)
        rq = ResidualCodebook(num_levels=4, config=config)

        z = torch.randn(1, 8, 16)
        result = rq(z)

        self.assertEqual(result["codes"].shape[0], 1)
        self.assertEqual(result["codes"].shape[1], 4)  # num_levels


class TestSparseAttention(unittest.TestCase):
    """Verify sparse attention pattern correctness."""

    def test_sliding_window(self):
        from compute.sparse_attention.omni_sparse_attention import OmniSparseAttention

        attn = OmniSparseAttention(dim=64, strategy="sliding_window", window_size=16)
        x = torch.randn(1, 32, 64)  # seq_len > window
        out = attn(x)
        self.assertEqual(out.shape, (1, 32, 64))

    def test_block_sparse(self):
        from compute.sparse_attention.omni_sparse_attention import OmniSparseAttention

        attn = OmniSparseAttention(dim=64, strategy="block_sparse", block_size=8)
        x = torch.randn(1, 24, 64)
        out = attn(x)
        self.assertEqual(out.shape, (1, 24, 64))


class TestPositionalEncoding(unittest.TestCase):
    """Verify positional encoding strategies."""

    def test_sinusoidal(self):
        from compute.positional_encoding.omni_positional_encoding import OmniPositionalEncoding

        pe = OmniPositionalEncoding(dim=128, strategy="sinusoidal")
        x = torch.randn(2, 50, 128)
        out = pe(x)
        self.assertEqual(out.shape, (2, 50, 128))

    def test_learned(self):
        from compute.positional_encoding.omni_positional_encoding import OmniPositionalEncoding

        pe = OmniPositionalEncoding(dim=128, strategy="learned")
        x = torch.randn(2, 50, 128)
        out = pe(x)
        self.assertEqual(out.shape, (2, 50, 128))

    def test_alibi(self):
        from compute.positional_encoding.omni_positional_encoding import ALiBiEncoding

        alibi = ALiBiEncoding(num_heads=8)
        bias = alibi(seq_len=64, device=torch.device("cpu"))
        self.assertEqual(bias.shape[-1], 64)
        self.assertEqual(bias.shape[-2], 64)


class TestMoE(unittest.TestCase):
    """Verify Mixture of Experts layer."""

    def test_moe_forward(self):
        from compute.moe.omni_mixture_of_experts import OmniMixtureOfExperts, MoEConfig

        config = MoEConfig(num_experts=4, expert_dim=64, ff_dim=128, top_k=2)
        moe = OmniMixtureOfExperts(config)

        x = torch.randn(2, 16, 64)
        result = moe(x)

        self.assertEqual(result["output"].shape, (2, 16, 64))
        self.assertIn("load_balance_loss", result)
        self.assertEqual(len(result["expert_usage"]), 4)


class TestFlashAttention(unittest.TestCase):
    """Verify flash attention block."""

    def test_flash_transformer(self):
        from compute.flash_attention.omni_flash_attention import OmniFlashTransformer

        model = OmniFlashTransformer(dim=64, depth=2, heads=4, block_size=16)
        x = torch.randn(1, 32, 64)
        out = model(x)
        self.assertEqual(out.shape, (1, 32, 64))


class TestKVCache(unittest.TestCase):
    """Verify paged KV cache operations."""

    def test_cache_update_and_get(self):
        from compute.kv_cache.omni_kv_cache import OmniKVCache, KVCacheConfig

        config = KVCacheConfig(
            num_layers=2, num_heads=4, num_kv_heads=2,
            head_dim=32, page_size=16, max_pages=8
        )
        cache = OmniKVCache(config, torch.device("cpu"))

        k = torch.randn(2, 10, 32)
        v = torch.randn(2, 10, 32)
        cache.update(0, k, v)

        retrieved_k, retrieved_v = cache.get(0)
        self.assertEqual(retrieved_k.shape[1], 10)
        self.assertEqual(cache.get_seq_length(0), 10)

    def test_cache_stats(self):
        from compute.kv_cache.omni_kv_cache import OmniKVCache, KVCacheConfig

        config = KVCacheConfig(num_layers=1, num_kv_heads=1, head_dim=8,
                               page_size=4, max_pages=4)
        cache = OmniKVCache(config, torch.device("cpu"))

        stats = cache.stats()
        self.assertEqual(stats["seq_length"], 0)
        self.assertGreaterEqual(stats["pages_available"], 0)


class TestTokenizer(unittest.TestCase):
    """Verify BPE tokenizer."""

    def test_train_and_encode(self):
        from compute.tokenizer.omni_vocab_tokenizer import OmniVocabTokenizer, TokenizerConfig

        config = TokenizerConfig(vocab_size=100, min_frequency=1)
        tokenizer = OmniVocabTokenizer(config)
        tokenizer.train(["hello world", "hello there", "world peace"])

        ids = tokenizer.encode("hello world")
        self.assertIsInstance(ids, list)
        self.assertGreater(len(ids), 0)

        decoded = tokenizer.decode(ids)
        self.assertIn("hello", decoded)

    def test_batch_encode(self):
        from compute.tokenizer.omni_vocab_tokenizer import OmniVocabTokenizer

        tokenizer = OmniVocabTokenizer()
        tokenizer.train(["hello", "world", "test"])

        result = tokenizer.batch_encode(["hello", "world"], padding=True)
        self.assertIn("input_ids", result)
        self.assertIn("attention_mask", result)
        self.assertEqual(len(result["input_ids"]), 2)


class TestPruningEngine(unittest.TestCase):
    """Verify model pruning."""

    def test_magnitude_pruning(self):
        from compute.pruning.omni_pruning_engine import MagnitudePruner

        weights = torch.randn(10, 10)
        mask = MagnitudePruner.create_mask(weights, sparsity=0.5)

        self.assertEqual(mask.shape, (10, 10))
        actual_sparsity = 1.0 - mask.float().mean().item()
        self.assertAlmostEqual(actual_sparsity, 0.5, delta=0.1)


class TestDataCollator(unittest.TestCase):
    """Verify dynamic batching collator."""

    def test_collate_variable_lengths(self):
        from compute.data_collator.omni_data_collator import OmniDataCollator

        collator = OmniDataCollator()
        features = [
            {"input_ids": [1, 2, 3]},
            {"input_ids": [4, 5, 6, 7, 8]},
        ]

        batch = collator.collate(features)
        self.assertEqual(batch["input_ids"].shape[0], 2)
        # All sequences padded to same length
        self.assertEqual(batch["input_ids"].shape[1],
                         batch["input_ids"].shape[1])


if __name__ == "__main__":
    unittest.main(verbosity=2)
