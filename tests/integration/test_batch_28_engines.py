import unittest
import sys
import os
import numpy as np

# Ensure paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/compute/python_core')))

from omni_phyx_reasoning_engine import OmniPhyxReasoningEngine
from omni_limoe_sparse_engine import OmniLimoeSparseEngine
from omni_deep_gcca_engine import OmniDeepGccaEngine
from omni_oakmower_spatial_engine import OmniOakmowerSpatialEngine
from omni_mmfakebench_misinfo_engine import OmniMmfakebenchMisinfoEngine
from omni_voicedevtools_realtime_engine import OmniVoicedevtoolsRealtimeEngine
from omni_onellm_unified_engine import OmniOnellmUnifiedEngine
from omni_weiclaw_gateway_engine import OmniWeiclawGatewayEngine
from omni_artraw_processing_engine import OmniArtRawProcessingEngine
from omni_visiongpt2_caption_engine import OmniVisionGpt2CaptionEngine
from omni_iisan_multimodal_rec_engine import OmniIisanMultimodalRecEngine
from omni_cnnlstm_caption_engine import OmniCnnLstmCaptionEngine
from omni_gemini_multimodal_chat_engine import OmniGeminiMultimodalChatEngine
from omni_hashtag_prediction_engine import OmniHashtagPredictionEngine
from omni_multieye_retinal_engine import OmniMultieyeRetinalEngine
from omni_chinese_vlbert_engine import OmniChineseVlbertEngine
from omni_reform_eval_engine import OmniReformEvalEngine
from omni_diffblender_diffusion_engine import OmniDiffblenderDiffusionEngine
from omni_ecommerce_embedding_engine import OmniEcommerceEmbeddingEngine
from omni_ecg_bench_analysis_engine import OmniEcgBenchAnalysisEngine
from omni_med_vqa_engine import OmniMedVqaEngine
from omni_layout_xlm_engine import OmniLayoutXlmEngine
from omni_dpr_retrieval_engine import OmniDprRetrievalEngine
from omni_cross_modal_hashing_engine import OmniCrossModalHashingEngine
from omni_video_instruct_engine import OmniVideoInstructEngine
from omni_trajectory_forecasting_engine import OmniTrajectoryForecastingEngine
from omni_timesformer_video_engine import OmniTimesformerVideoEngine
from omni_pointnet_grasp_engine import OmniPointnetGraspEngine
from omni_audio_separation_engine import OmniAudioSeparationEngine
from omni_federated_learning_engine import OmniFederatedLearningEngine

class TestBatch28Engines(unittest.TestCase):

    def test_phyx(self):
        engine = OmniPhyxReasoningEngine()
        payload = {
            "predicted_motion": np.random.randn(2, 5, 3).tolist(),
            "ground_physics": np.random.randn(2, 5, 3).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)
        self.assertIn("is_physically_plausible", res.value)

    def test_limoe(self):
        engine = OmniLimoeSparseEngine()
        payload = {"expert_logits": np.random.randn(4, 10).tolist()}
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_deep_gcca(self):
        engine = OmniDeepGccaEngine()
        payload = {
            "semantic_view_a": np.random.randn(8, 32).tolist(),
            "semantic_view_b": np.random.randn(8, 32).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_oakmower(self):
        engine = OmniOakmowerSpatialEngine()
        payload = {
            "spatial_coordinate_sequence": np.random.uniform(0, 10, size=(20, 2)).tolist(),
            "map_bounds": [10, 10]
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_mmfakebench(self):
        engine = OmniMmfakebenchMisinfoEngine()
        payload = {
            "text_semantic_latent": np.random.randn(2, 64).tolist(),
            "visual_evidence_latent": np.random.randn(2, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_voice_devtools(self):
        engine = OmniVoicedevtoolsRealtimeEngine()
        payload = {
            "ingest_timestamps_ms": [100.0, 200.0, 300.0],
            "response_timestamps_ms": [150.0, 260.0, 340.0]
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_onellm(self):
        engine = OmniOnellmUnifiedEngine()
        payload = {"sensory_tensor": np.random.randn(4, 1024).tolist()}
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_weiclaw(self):
        engine = OmniWeiclawGatewayEngine()
        payload = {
            "historical_load": np.random.poisson(10, size=(20,)).tolist(),
            "node_capacities": np.array([100.0, 200.0, 150.0]).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_artraw(self):
        engine = OmniArtRawProcessingEngine()
        payload = {"raw_bayer_tensor": np.random.uniform(0, 1, size=(32, 32)).tolist()}
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_visiongpt2(self):
        engine = OmniVisionGpt2CaptionEngine()
        payload = {
            "autoregressive_logits": np.random.randn(10, 5000).tolist(),
            "target_indices": np.random.randint(0, 5000, size=(10,)).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_iisan(self):
        engine = OmniIisanMultimodalRecEngine()
        payload = {
            "sequence_embeddings": np.random.randn(2, 5, 64).tolist(),
            "time_deltas": np.random.uniform(0.1, 5.0, size=(2, 5)).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_cnnlstm(self):
        engine = OmniCnnLstmCaptionEngine()
        payload = {
            "cnn_features": np.random.randn(2, 128).tolist(),
            "lstm_forget": np.random.randn(2, 10, 128).tolist(),
            "lstm_input": np.random.randn(2, 10, 128).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_gemini(self):
        engine = OmniGeminiMultimodalChatEngine()
        payload = {
            "sequence_text_embeddings": np.random.randn(2, 5, 256).tolist(),
            "multimodal_context_embeddings": np.random.randn(2, 3, 256).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_hashtag(self):
        engine = OmniHashtagPredictionEngine()
        payload = {"tag_adjacency_matrices": np.random.uniform(0, 1, size=(2, 10, 10)).tolist()}
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_multieye(self):
        engine = OmniMultieyeRetinalEngine()
        payload = {
            "fundus_2d_latents": np.random.randn(2, 64).tolist(),
            "oct_3d_volume": np.random.randn(2, 10, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_chinesevlbert(self):
        engine = OmniChineseVlbertEngine()
        payload = {
            "visual_region_latents": np.random.randn(2, 5, 128).tolist(),
            "hanzi_lexical_latents": np.random.randn(2, 10, 128).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_reform_eval(self):
        engine = OmniReformEvalEngine()
        payload = {
            "baseline_text_logits": np.random.randn(2, 5000).tolist(),
            "perturbed_text_logits": np.random.randn(2, 5000).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_diffblender(self):
        engine = OmniDiffblenderDiffusionEngine()
        payload = {
            "latent_prior_a": np.random.randn(2, 4, 16, 16).tolist(),
            "latent_prior_b": np.random.randn(2, 4, 16, 16).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_ecommerce(self):
        engine = OmniEcommerceEmbeddingEngine()
        payload = {
            "query_dense_latent": np.random.randn(2, 128).tolist(),
            "document_dense_latents": np.random.randn(2, 10, 128).tolist(),
            "lexical_overlap": np.random.uniform(0, 1, size=(2, 10)).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_ecgbench(self):
        engine = OmniEcgBenchAnalysisEngine()
        payload = {"ecg_temporal_leads": np.random.randn(2, 50, 12).tolist()}
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_medvqa(self):
        engine = OmniMedVqaEngine()
        payload = {
            "radiology_feature_grid": np.random.randn(2, 49, 128).tolist(),
            "clinical_query_latent": np.random.randn(2, 128).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_layoutxlm(self):
        engine = OmniLayoutXlmEngine()
        payload = {
            "semantic_text_embeddings": np.random.randn(2, 20, 256).tolist(),
            "document_bounding_boxes": np.random.uniform(0, 1000, size=(2, 20, 4)).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_dpr(self):
        engine = OmniDprRetrievalEngine()
        payload = {
            "query_embeddings": np.random.randn(2, 128).tolist(),
            "passage_embeddings": np.random.randn(10, 128).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_crosshash(self):
        engine = OmniCrossModalHashingEngine()
        payload = {
            "query_continuous": np.random.randn(2, 64).tolist(),
            "database_continuous": np.random.randn(10, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_videoinstruct(self):
        engine = OmniVideoInstructEngine()
        payload = {
            "video_frame_latency": np.random.randn(2, 10, 128).tolist(),
            "instruction_latent": np.random.randn(2, 128).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_trajforecasting(self):
        engine = OmniTrajectoryForecastingEngine()
        payload = {"historical_trajectories": np.random.randn(2, 5, 2).tolist()}
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_timesformer(self):
        engine = OmniTimesformerVideoEngine()
        payload = {
            "spatial_patch_tokens": np.random.randn(2, 8, 16, 64).tolist(),
            "temporal_patch_tokens": np.random.randn(2, 16, 8, 64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_pointnet(self):
        engine = OmniPointnetGraspEngine()
        payload = {
            "point_cloud_geometry": np.random.randn(2, 50, 3).tolist(),
            "grasp_approaches": np.random.randn(2, 10, 3).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_audiosep(self):
        engine = OmniAudioSeparationEngine()
        payload = {
            "complex_mixture_spectrogram": np.random.randn(2, 64, 64).astype(np.complex64).tolist(),
            "source_spectral_estimations": np.random.randn(2, 3, 64, 64).astype(np.complex64).tolist()
        }
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

    def test_federated(self):
        engine = OmniFederatedLearningEngine()
        payload = {"node_gradient_updates": np.random.randn(10, 512).tolist()}
        res = engine.process(payload)
        self.assertTrue(res.is_ok)

if __name__ == '__main__':
    unittest.main()
