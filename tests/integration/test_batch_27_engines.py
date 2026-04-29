import os
import sys
import unittest
import numpy as np

# Ensure module path is appended
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/compute/python_core')))

from omni_qstar_search_engine import OmniQstarSearchEngine
from omni_hyperbolic_embedding_engine import OmniHyperbolicEmbeddingEngine
from omni_retnet_retention_engine import OmniRetnetRetentionEngine
from omni_sora_video_diffusion_engine import OmniSoraVideoDiffusionEngine
from omni_mamba_state_space_engine import OmniMambaStateSpaceEngine
from omni_jepa_predictive_arch_engine import OmniJepaPredictiveArchEngine
from omni_kan_network_engine import OmniKanNetworkEngine
from omni_timesfm_forecasting_engine import OmniTimesfmForecastingEngine
from omni_siglip_visual_alignment_engine import OmniSiglipVisualAlignmentEngine
from omni_grok_moe_routing_engine import OmniGrokMoeRoutingEngine
from omni_lwm_long_context_engine import OmniLwmLongContextEngine
from omni_dspy_program_optimization_engine import OmniDspyProgramOptimizationEngine
from omni_voyager_embodied_agent_engine import OmniVoyagerEmbodiedAgentEngine
from omni_alphageometry_reasoning_engine import OmniAlphageometryReasoningEngine
from omni_codellama_infilling_engine import OmniCodellamaInfillingEngine
from omni_dalle3_caption_upsampling_engine import OmniDalle3CaptionUpsamplingEngine
from omni_qwen_vl_grounding_engine import OmniQwenVlGroundingEngine
from omni_moondream_edge_vision_engine import OmniMoondreamEdgeVisionEngine
from omni_pixtral_multimodal_interleaving_engine import OmniPixtralMultimodalInterleavingEngine
from omni_gpt4o_audio_visual_sync_engine import OmniGpt4oAudioVisualSyncEngine
from omni_command_r_tool_use_engine import OmniCommandRToolUseEngine
from omni_llama3_reinforcement_alignment_engine import OmniLlama3ReinforcementAlignmentEngine
from omni_phi3_synthetic_distillation_engine import OmniPhi3SyntheticDistillationEngine
from omni_qwen2_math_reasoning_engine import OmniQwen2MathReasoningEngine
from omni_mixtral_sparse_routing_engine import OmniMixtralSparseRoutingEngine
from omni_deepmind_synthid_watermark_engine import OmniDeepmindSynthidWatermarkEngine
from omni_gemini_pro_multimodal_routing_engine import OmniGeminiProMultimodalRoutingEngine
from omni_claude3_opus_metacognitive_engine import OmniClaude3OpusMetacognitiveEngine
from omni_stable_audio_latent_engine import OmniStableAudioLatentEngine
from omni_aya_multilingual_alignment_engine import OmniAyaMultilingualAlignmentEngine

class TestBatch27Engines(unittest.TestCase):

    def test_qstar_search_engine(self):
        engine = OmniQstarSearchEngine()
        payload = {
            "policy_priors": np.random.rand(10).tolist(),
            "state_values": np.random.rand(10).tolist(),
            "step_cost": 0.5
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("max_expected_q", res.value)

    def test_hyperbolic_embedding_engine(self):
        engine = OmniHyperbolicEmbeddingEngine()
        payload = {
            "source_embedding": np.random.randn(5, 16).tolist(),
            "target_embedding": np.random.randn(5, 16).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("hyperbolic_distance_matrix", res.value)

    def test_retnet_retention_engine(self):
        engine = OmniRetnetRetentionEngine()
        payload = {
            "queries": np.random.randn(2, 5, 8).tolist(),
            "keys": np.random.randn(2, 5, 8).tolist(),
            "values": np.random.randn(2, 5, 8).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["retained_outputs"]).shape, (2, 5, 8))

    def test_sora_video_diffusion_engine(self):
        engine = OmniSoraVideoDiffusionEngine()
        payload = {
            "spatiotemporal_latents": np.random.randn(4, 10, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("is_spatiotemporally_coherent", res.value)

    def test_mamba_state_space_engine(self):
        engine = OmniMambaStateSpaceEngine()
        payload = {
            "x_sequence": np.random.randn(20).tolist(),
            "matrix_a": np.random.randn(8, 8).tolist(),
            "vector_b": np.random.randn(8).tolist(),
            "vector_c": np.random.randn(8).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["discretized_scan_output"]).shape, (20,))

    def test_jepa_predictive_arch_engine(self):
        engine = OmniJepaPredictiveArchEngine()
        payload = {
            "context_prediction": np.random.randn(8, 64).tolist(),
            "target_representation": np.random.randn(8, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("latent_alignment_energy", res.value)

    def test_kan_network_engine(self):
        engine = OmniKanNetworkEngine()
        payload = {
            "edge_inputs": np.random.randn(4, 10).tolist(),
            "spline_coefficients": np.random.randn(10, 5, 5).tolist() # (In, Out, Grid)
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["kan_resolved_outputs"]).shape, (4, 5))

    def test_timesfm_forecasting_engine(self):
        engine = OmniTimesfmForecastingEngine()
        payload = {
            "context_series": np.random.randn(3, 100).tolist(),
            "forecast_horizon": 24
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["multi_horizon_predictions"]).shape, (3, 24))

    def test_siglip_visual_alignment_engine(self):
        engine = OmniSiglipVisualAlignmentEngine()
        payload = {
            "image_embeddings": np.random.randn(16, 128).tolist(),
            "text_embeddings": np.random.randn(16, 128).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["siglip_pairwise_probabilities"]).shape, (16, 16))

    def test_grok_moe_routing_engine(self):
        engine = OmniGrokMoeRoutingEngine()
        payload = {
            "hidden_tokens": np.random.randn(2, 64, 128).tolist(),
            "gate_weights": np.random.randn(128, 8).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["expert_routing_probabilities"]).shape, (2, 64, 8))

    def test_lwm_long_context_engine(self):
        engine = OmniLwmLongContextEngine()
        payload = {
            "hidden_states": np.random.randn(2, 100, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["rotated_embeddings"]).shape, (2, 100, 64))

    def test_dspy_program_optimization_engine(self):
        engine = OmniDspyProgramOptimizationEngine()
        payload = {
            "prompt_signature_weights": np.random.randn(10, 64).tolist(),
            "metric_deviations": np.random.randn(10, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("optimized_signature_weights", res.value)

    def test_voyager_embodied_agent_engine(self):
        engine = OmniVoyagerEmbodiedAgentEngine()
        payload = {
            "skill_embedding": np.random.randn(1, 128).tolist(),
            "skill_library": np.random.randn(50, 128).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("is_skill_novel", res.value)

    def test_alphageometry_reasoning_engine(self):
        engine = OmniAlphageometryReasoningEngine()
        payload = {
            "point_a": np.random.randn(5, 2).tolist(),
            "point_b": np.random.randn(5, 2).tolist(),
            "point_c": np.random.randn(5, 2).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("is_collinear_theorem", res.value)

    def test_codellama_infilling_engine(self):
        engine = OmniCodellamaInfillingEngine()
        payload = {
            "prefix_boundary_logits": np.random.randn(4, 1024).tolist(),
            "suffix_boundary_logits": np.random.randn(4, 1024).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("fim_continuity_divergence", res.value)

    def test_dalle3_caption_upsampling_engine(self):
        engine = OmniDalle3CaptionUpsamplingEngine()
        payload = {
            "base_caption_embeddings": np.random.randn(4, 16).tolist(),
            "expansion_manifold": np.random.randn(16, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["upsampled_caption_embeddings"]).shape, (4, 64))

    def test_qwen_vl_grounding_engine(self):
        engine = OmniQwenVlGroundingEngine()
        payload = {
            "region_heatmaps": np.random.randn(3, 256, 32).tolist(),
            "text_entity_embedding": np.random.randn(3, 32).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["normalized_grounding_boxes"]).shape, (3, 4))

    def test_moondream_edge_vision_engine(self):
        engine = OmniMoondreamEdgeVisionEngine()
        payload = {
            "vision_features": np.random.randn(2, 50, 128).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["edge_optimized_features"]).shape, (2, 50, 32))

    def test_pixtral_multimodal_interleaving_engine(self):
        engine = OmniPixtralMultimodalInterleavingEngine()
        payload = {
            "text_embeddings": np.random.randn(10, 64).tolist(),
            "image_embeddings": np.random.randn(4, 64).tolist(),
            "interleave_mask": [0, 1, 0, 0, 1, 0, 1, 0, 0, 1]
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["interleaved_multimodal_sequence"]).shape, (10, 64))

    def test_gpt4o_audio_visual_sync_engine(self):
        engine = OmniGpt4oAudioVisualSyncEngine()
        payload = {
            "audio_stream": np.random.randn(100, 32).tolist(),
            "video_stream": np.random.randn(100, 32).tolist(),
            "text_stream": np.random.randn(100, 32).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["temporal_phase_locks"]).shape, (100,))

    def test_command_r_tool_use_engine(self):
        engine = OmniCommandRToolUseEngine()
        payload = {
            "claim_embeddings": np.random.randn(3, 64).tolist(),
            "tool_doc_embeddings": np.random.randn(10, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["claim_grounding_scores"]).shape, (3,))

    def test_llama3_reinforcement_alignment_engine(self):
        engine = OmniLlama3ReinforcementAlignmentEngine()
        payload = {
            "sequence_rewards": np.random.randn(2, 50).tolist(),
            "state_values": np.random.randn(2, 50).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["generalized_advantage_estimations"]).shape, (2, 50))

    def test_phi3_synthetic_distillation_engine(self):
        engine = OmniPhi3SyntheticDistillationEngine()
        payload = {
            "document_corpus_embeddings": np.random.randn(20, 128).tolist(),
            "textbook_attractor_embedding": np.random.randn(128).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("distilled_document_count", res.value)

    def test_qwen2_math_reasoning_engine(self):
        engine = OmniQwen2MathReasoningEngine()
        payload = {
            "derivation_steps": [np.random.randn(1, 64).tolist() for _ in range(5)],
            "final_answer": np.random.randn(1, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("cot_consistency_margin", res.value)

    def test_mixtral_sparse_routing_engine(self):
        engine = OmniMixtralSparseRoutingEngine(top_k=2)
        payload = {
            "token_routing_logits": np.random.randn(10, 8).tolist() # 10 tokens, 8 experts
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["sparse_capacity_bounded_assignments"]).shape, (10, 8))

    def test_deepmind_synthid_watermark_engine(self):
        engine = OmniDeepmindSynthidWatermarkEngine()
        payload = {
            "host_signal": np.random.randn(2, 1024).tolist(),
            "watermark_signature": np.random.randn(2, 32).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["synthid_watermarked_signal"]).shape, (2, 1024))

    def test_gemini_pro_multimodal_routing_engine(self):
        engine = OmniGeminiProMultimodalRoutingEngine()
        payload = {
            "logits_vision": np.random.randn(2, 10, 128).tolist(),
            "logits_audio": np.random.randn(2, 10, 128).tolist(),
            "logits_text": np.random.randn(2, 10, 128).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["fused_multimodal_logits"]).shape, (2, 10, 128))

    def test_claude3_opus_metacognitive_engine(self):
        engine = OmniClaude3OpusMetacognitiveEngine()
        payload = {
            "query_embedding": np.random.randn(2, 64).tolist(),
            "constitutional_rule_embeddings": np.random.randn(10, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["max_constitutional_violation_scores"]).shape, (2,))

    def test_stable_audio_latent_engine(self):
        engine = OmniStableAudioLatentEngine()
        payload = {
            "latent_chunk_a": np.random.randn(4, 50, 128).tolist(),
            "latent_chunk_b": np.random.randn(4, 50, 128).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("audio_latent_continuity_score", res.value)

    def test_aya_multilingual_alignment_engine(self):
        engine = OmniAyaMultilingualAlignmentEngine()
        payload = {
            "source_language_embeddings": np.random.randn(5, 64).tolist(),
            "target_language_embeddings": np.random.randn(5, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["pairwise_cross_lingual_symmetry"]).shape, (5,))

if __name__ == '__main__':
    unittest.main()
