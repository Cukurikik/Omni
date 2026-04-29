import os
import sys
import unittest
import numpy as np

# Ensure module path is appended
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/compute/python_core')))

from omni_causal_mm_attention_engine import OmniCausalMmAttentionEngine
from omni_generative_dl_diffusion_engine import OmniGenerativeDlDiffusionEngine
from omni_mmcows_tracking_engine import OmniMmcowsTrackingEngine
from omni_visual_web_bench_eval_engine import OmniVisualWebBenchEvalEngine
from omni_cross_the_gap_inversion_engine import OmniCrossTheGapInversionEngine
from omni_azure_ai_multimodal_rag_engine import OmniAzureAiMultimodalRagEngine
from omni_cortex_prompt_execution_engine import OmniCortexPromptExecutionEngine
from omni_graph_distillation_action_engine import OmniGraphDistillationActionEngine
from omni_harma_modality_alignment_engine import OmniHarmaModalityAlignmentEngine
from omni_r1_track_reinforcement_engine import OmniR1TrackReinforcementEngine
from omni_vlm_finetuning_pipeline_engine import OmniVlmFinetuningPipelineEngine
from omni_multimodal_recommender_engine import OmniMultimodalRecommenderEngine
from omni_adviser_task_dialog_engine import OmniAdviserTaskDialogEngine
from omni_deepslide_presentation_engine import OmniDeepslidePresentationEngine
from omni_omega_bittensor_subnet_engine import OmniOmegaBittensorSubnetEngine
from omni_citrus_farm_multimodal_engine import OmniCitrusFarmMultimodalEngine
from omni_rllava_multimodal_rl_engine import OmniRllavaMultimodalRlEngine
from omni_ner_multimodal_coattention_engine import OmniNerMultimodalCoattentionEngine
from omni_brats_tumor_segmentation_engine import OmniBratsTumorSegmentationEngine
from omni_omnicourse_lecture_vision_engine import OmniOmnicourseLectureVisionEngine
from omni_pki_mllm_knowledge_engine import OmniPkiMllmKnowledgeEngine
from omni_m2pt_multimodal_prompting_engine import OmniM2ptMultimodalPromptingEngine
from omni_mllm_watermark_detection_engine import OmniMllmWatermarkDetectionEngine
from omni_ritcv_infra_engine import OmniRitcvInfraEngine
from omni_causal_prompt_reasoning_engine import OmniCausalPromptReasoningEngine
from omni_gpt_sovits_webui_engine import OmniGptSovitsWebUiEngine
from omni_mmpose_estimator_engine import OmniMmposeEstimatorEngine
from omni_omniedge_compression_engine import OmniOmniedgeCompressionEngine
from omni_llava_visual_instruct_engine import OmniLlavaVisualInstructEngine
from omni_batav_vision_tracking_engine import OmniBatavVisionTrackingEngine

from omni_adviser_task_dialog_engine import OmniAdviserTaskDialogEngine
from omni_deepslide_presentation_engine import OmniDeepslidePresentationEngine
from omni_omega_bittensor_subnet_engine import OmniOmegaBittensorSubnetEngine

class TestBatch26Engines(unittest.TestCase):

    def test_causal_mm_attention_engine(self):
        engine = OmniCausalMmAttentionEngine()
        payload = {
            "query_states": np.random.rand(10, 16, 64).tolist(),
            "key_states": np.random.rand(10, 16, 64).tolist(),
            "value_states": np.random.rand(10, 16, 64).tolist(),
            "modality_mask": np.random.randint(0, 2, size=(10, 1)).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("counterfactual_attention_out", res.value)

    def test_generative_dl_diffusion_engine(self):
        engine = OmniGenerativeDlDiffusionEngine()
        payload = {
            "latent_image": np.random.randn(2, 3, 64, 64).tolist(),
            "timestep": [100, 500]
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("noised_latent", res.value)
        self.assertEqual(np.array(res.value["noised_latent"]).shape, (2, 3, 64, 64))

    def test_mmcows_tracking_engine(self):
        engine = OmniMmcowsTrackingEngine()
        payload = {
            "state": [0.0, 0.0, 1.0, 1.0],
            "covariance": np.eye(4).tolist(),
            "uwb_distance": 5.0,
            "visual_position": [4.5, 4.5]
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("fused_state", res.value)

    def test_visual_web_bench_eval_engine(self):
        engine = OmniVisualWebBenchEvalEngine()
        payload = {
            "predicted_boxes": [
                [10.0, 10.0, 50.0, 50.0],
                [100.0, 100.0, 120.0, 120.0]
            ],
            "ground_truth_boxes": [
                [11.0, 11.0, 51.0, 51.0],
                [200.0, 200.0, 250.0, 250.0]
            ]
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("iou_matrix", res.value)
        self.assertGreaterEqual(res.value["hits"], 1)

    def test_cross_the_gap_inversion_engine(self):
        engine = OmniCrossTheGapInversionEngine()
        payload = {
            "source_embeddings": np.random.randn(4, 128).tolist(),
            "target_embeddings": np.random.randn(4, 128).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("inversion_alignment_score", res.value)

    def test_azure_ai_multimodal_rag_engine(self):
        engine = OmniAzureAiMultimodalRagEngine(top_k=2)
        payload = {
            "query_embedding": np.random.randn(2, 64).tolist(),
            "document_embeddings": np.random.randn(10, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("retrieved_indices", res.value)
        self.assertEqual(len(res.value["retrieved_indices"][0]), 2)

    def test_cortex_prompt_execution_engine(self):
        engine = OmniCortexPromptExecutionEngine()
        payload = {
            "prompt_template": "Calculate {{x}} and verify {{y}}.",
            "context": {"x": 50, "y": 100}
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(res.value["executed_prompt"], "Calculate 50 and verify 100.")

    def test_graph_distillation_action_engine(self):
        engine = OmniGraphDistillationActionEngine()
        payload = {
            "teacher_graph_logits": np.random.randn(5, 10).tolist(),
            "student_graph_logits": np.random.randn(5, 10).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("distillation_kl_loss", res.value)

    def test_harma_modality_alignment_engine(self):
        engine = OmniHarmaModalityAlignmentEngine()
        payload = {
            "optical_features": np.random.randn(100, 32).tolist(),
            "sar_features": np.random.randn(100, 32).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["aligned_optical_features"]).shape, (100, 32))

    def test_r1_track_reinforcement_engine(self):
        engine = OmniR1TrackReinforcementEngine()
        payload = {
            "rewards": np.random.randn(10, 5).tolist(),
            "log_probs": np.random.randn(10, 5).tolist(),
            "old_log_probs": np.random.randn(10, 5).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("grpo_surrogate_loss", res.value)

    def test_vlm_finetuning_pipeline_engine(self):
        engine = OmniVlmFinetuningPipelineEngine()
        payload = {
            "w_base": np.random.randn(64, 64).tolist(),
            "x_input": np.random.randn(4, 64).tolist(),
            "lora_a": np.random.randn(64, 8).tolist(),
            "lora_b": np.random.randn(8, 64).tolist(),
            "loss_gradients": np.random.randn(4, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("output_activations", res.value)

    def test_multimodal_recommender_engine(self):
        engine = OmniMultimodalRecommenderEngine()
        payload = {
            "user_embeddings": np.random.randn(10, 32).tolist(),
            "item_embeddings": np.random.randn(20, 32).tolist(),
            "visual_features": np.random.randn(20, 32).tolist(),
            "text_features": np.random.randn(20, 32).tolist(),
            "user_vis_pref": np.random.randn(10, 32).tolist(),
            "user_txt_pref": np.random.randn(10, 32).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["recommender_scores"]).shape, (10, 20))

    def test_adviser_task_dialog_engine(self):
        engine = OmniAdviserTaskDialogEngine()
        payload = {
            "prior_belief": np.random.rand(4, 10).tolist(),
            "transition_matrix": np.random.rand(4, 10, 10).tolist(),
            "observation_likelihoods": np.random.rand(4, 10).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("posterior_belief", res.value)

    def test_deepslide_presentation_engine(self):
        engine = OmniDeepslidePresentationEngine(pacing_threshold=0.1)
        payload = {
            "agent_transition_votes": np.random.randn(5, 10).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(len(res.value["trigger_flags"]), 10)

    def test_omega_bittensor_subnet_engine(self):
        engine = OmniOmegaBittensorSubnetEngine()
        payload = {
            "miner_predictions": np.random.randn(15, 64).tolist(),
            "ground_truth": np.random.randn(64).tolist(),
            "historic_weights": np.random.rand(15).tolist(),
            "response_latency": np.random.rand(15).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("updated_subnet_weights", res.value)

    def test_citrus_farm_multimodal_engine(self):
        engine = OmniCitrusFarmMultimodalEngine()
        payload = {
            "rgb_features": np.random.randn(8, 128).tolist(),
            "depth_features": np.random.randn(8, 128).tolist(),
            "thermal_features": np.random.randn(8, 128).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("fused_features", res.value)
        self.assertEqual(np.array(res.value["fused_features"]).shape, (8, 128))

    def test_rllava_multimodal_rl_engine(self):
        engine = OmniRllavaMultimodalRlEngine()
        payload = {
            "policy_chosen": np.random.randn(10).tolist(),
            "policy_rejected": np.random.randn(10).tolist(),
            "ref_chosen": np.random.randn(10).tolist(),
            "ref_rejected": np.random.randn(10).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("dpo_loss", res.value)

    def test_ner_multimodal_coattention_engine(self):
        engine = OmniNerMultimodalCoattentionEngine(hidden_dim=32)
        payload = {
            "text_embeddings": np.random.randn(15, 32).tolist(),
            "visual_embeddings": np.random.randn(5, 32).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["fused_tokens"]).shape, (15, 32))

    def test_brats_tumor_segmentation_engine(self):
        engine = OmniBratsTumorSegmentationEngine()
        payload = {
            "predicted_volumes": np.random.rand(2, 4, 32, 32).tolist(),
            "ground_truth_volumes": np.random.randint(0, 2, size=(2, 4, 32, 32)).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("mean_dice", res.value)

    def test_omnicourse_lecture_vision_engine(self):
        engine = OmniOmnicourseLectureVisionEngine()
        payload = {
            "transcript_embeddings": np.random.randn(20, 64).tolist(),
            "keyframe_embeddings": np.random.randn(5, 64).tolist(),
            "alignment_weights": np.random.rand(20, 5).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("lecture_multimodal_embeddings", res.value)
        self.assertEqual(np.array(res.value["lecture_multimodal_embeddings"]).shape, (20, 64))

    def test_pki_mllm_knowledge_engine(self):
        engine = OmniPkiMllmKnowledgeEngine()
        payload = {
            "visual_embeddings": np.random.randn(10, 64).tolist(),
            "knowledge_embeddings": np.random.randn(10, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("pki_modulated_visuals", res.value)

    def test_m2pt_multimodal_prompting_engine(self):
        engine = OmniM2ptMultimodalPromptingEngine()
        payload = {
            "original_attention_state": np.random.rand(4, 16, 64).tolist(),
            "tuned_attention_state": (np.random.rand(4, 16, 64) + 0.1).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("attention_drift_magnitude", res.value)

    def test_mllm_watermark_detection_engine(self):
        engine = OmniMllmWatermarkDetectionEngine()
        payload = {
            "visual_signal_matrix": np.random.randn(64, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("watermark_present", res.value)

    def test_ritcv_infra_engine(self):
        engine = OmniRitcvInfraEngine()
        payload = {
            "spatial_points": np.random.rand(10, 3).tolist(),
            "camera_intrinsics": {"focal_length": 500.0, "cx": 320.0, "cy": 240.0}
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("projected_2d_pixels", res.value)

    def test_causal_prompt_reasoning_engine(self):
        engine = OmniCausalPromptReasoningEngine()
        payload = {
            "baseline_probabilities": np.random.rand(5, 100).tolist(),
            "intervention_probabilities": np.random.rand(5, 100).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("mean_causal_effect", res.value)

    def test_gpt_sovits_webui_engine(self):
        engine = OmniGptSovitsWebUiEngine()
        payload = {
            "text_acoustic_tokens": np.random.randn(2, 50, 64).tolist(),
            "reference_speaker_tokens": np.random.randn(2, 20, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("synthesized_voice_tokens", res.value)
        self.assertEqual(np.array(res.value["synthesized_voice_tokens"]).shape, (2, 50, 64))

    def test_mmpose_estimator_engine(self):
        engine = OmniMmposeEstimatorEngine()
        payload = {
            "heatmaps": np.random.randn(4, 17, 64, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("keypoint_coordinates", res.value)
        self.assertEqual(np.array(res.value["keypoint_coordinates"]).shape, (4, 17, 2))

    def test_omniedge_compression_engine(self):
        engine = OmniOmniedgeCompressionEngine()
        payload = {
            "fp32_weights": np.random.randn(100, 100).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("quantized_int8_weights", res.value)

    def test_llava_visual_instruct_engine(self):
        engine = OmniLlavaVisualInstructEngine()
        payload = {
            "vision_tokens": np.random.randn(256, 128).tolist(),
            "mlp_weights": np.random.randn(512, 128).tolist(),
            "mlp_bias": np.random.randn(512).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertEqual(np.array(res.value["pseudo_text_tokens"]).shape, (256, 512))

    def test_batav_vision_tracking_engine(self):
        engine = OmniBatavVisionTrackingEngine()
        payload = {
            "predicted_box": [10.0, 10.0, 50.0, 50.0],
            "detected_box": [12.0, 12.0, 48.0, 48.0]
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("fused_tracking_box", res.value)

if __name__ == '__main__':
    unittest.main()
