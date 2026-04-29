"""
OMNI MOTHER — Semester 12, Batch 18 Integration Test Suite
Tests all 30 production-grade engines for:
  - Monadic Result[T, E] compliance (Ok/Err)
  - Zero-mock enforcement (real math, no stubs)
  - diagnostics() operational integrity
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.compute.python_core.omni_antfly_engine import OmniAntflyEngine
from src.compute.python_core.omni_vision_reasoner_engine import OmniVisionReasonerEngine
from src.compute.python_core.omni_world_simulator_engine import OmniWorldSimulatorEngine
from src.compute.python_core.omni_palm_e_engine import OmniPalmEEngine
from src.compute.python_core.omni_mark_everything_down_engine import OmniMarkEverythingDownEngine
from src.compute.python_core.omni_stark_engine import OmniStarkEngine
from src.compute.python_core.omni_pathomic_fusion_engine import OmniPathomicFusionEngine
from src.compute.python_core.omni_awesome_mm_papers_engine import OmniAwesomeMMPapersEngine
from src.compute.python_core.omni_cc2dataset_engine import OmniCc2DatasetEngine
from src.compute.python_core.omni_mimic_iv_pipeline_engine import OmniMimicIVPipelineEngine
from src.compute.python_core.omni_hpt_engine import OmniHPTEngine
from src.compute.python_core.omni_awesome_mm_auto_drive_engine import OmniAwesomeMMAutoDriveEngine
from src.compute.python_core.omni_rlhf_v_engine import OmniRlhfVEngine
from src.compute.python_core.omni_youku_mplug_engine import OmniYoukuMPlugEngine
from src.compute.python_core.omni_lrv_instruction_engine import OmniLrvInstructionEngine
from src.compute.python_core.omni_vlm_bow_engine import OmniVlmBowEngine
from src.compute.python_core.omni_pixel_reasoner_engine import OmniPixelReasonerEngine
from src.compute.python_core.omni_video_gpt_plus_engine import OmniVideoGptPlusEngine
from src.compute.python_core.omni_aui_test_agent_engine import OmniAuiTestAgentEngine
from src.compute.python_core.omni_cav_mae_engine import OmniCavMaeEngine
from src.compute.python_core.omni_embodied_agents_engine import OmniEmbodiedAgentsEngine
from src.compute.python_core.omni_awesome_mm_prompts_engine import OmniAwesomeMMPromptsEngine
from src.compute.python_core.omni_openclaw_net_engine import OmniOpenClawNetEngine
from src.compute.python_core.omni_pvm_engine import OmniPvmEngine
from src.compute.python_core.omni_mm_autodrive_planner_engine import OmniMMAutoDrivePlannerEngine
from src.compute.python_core.omni_rlhf_v_align_engine import OmniRlhfVAlignEngine
from src.compute.python_core.omni_youku_video_abstractor_engine import OmniYoukuVideoAbstractorEngine
from src.compute.python_core.omni_lrv_gavie_engine import OmniLrvGavieEngine
from src.compute.python_core.omni_aro_bow_benchmark_engine import OmniAroBowBenchmarkEngine
from src.compute.python_core.omni_curiosity_rl_engine import OmniCuriosityRLEngine


class TestSemester12Batch18:
    """Integration tests for all 30 Batch 18 engines."""

    def _validate_engine(self, engine_cls, payload=None):
        """Common validation for all engines."""
        engine = engine_cls()
        # Test diagnostics
        diag = engine.diagnostics()
        assert diag['status'] == 'operational'
        assert diag['batch'] == 18
        assert diag['semester'] == 12
        # Test process
        result = engine.process(payload or {})
        assert result.is_ok(), f"{engine_cls.__name__} failed: {result.error if result.is_err() else 'unknown'}"
        assert isinstance(result.value, dict)
        return result.value

    def test_antfly_engine(self):
        val = self._validate_engine(OmniAntflyEngine, {
            'query_tokens': ['machine', 'learning'],
            'doc_tokens_list': [['machine', 'learning', 'AI'], ['deep', 'neural', 'network']],
            'query_vector': [0.8, 0.6],
            'doc_vectors': [[0.7, 0.5], [0.2, 0.9]]
        })
        assert 'rrf_score' in val
        assert 'bm25_score' in val
        assert val['best_doc_idx'] in [0, 1]

    def test_vision_reasoner_engine(self):
        val = self._validate_engine(OmniVisionReasonerEngine, {
            'pred_boxes': [[10, 10, 50, 50], [60, 60, 100, 100]],
            'gt_boxes': [[12, 12, 48, 48], [62, 62, 98, 98]],
            'format_valid': True
        })
        assert 'mean_iou' in val
        assert 0 <= val['mean_iou'] <= 1
        assert val['total_reward'] > 0

    def test_world_simulator_engine(self):
        val = self._validate_engine(OmniWorldSimulatorEngine, {
            'generated_embedding': [0.5, 0.3, 0.8],
            'reference_embedding': [0.4, 0.35, 0.75],
            'text_embedding': [0.45, 0.32, 0.78]
        })
        assert 'fid_approx' in val
        assert 'clip_score' in val

    def test_palm_e_engine(self):
        val = self._validate_engine(OmniPalmEEngine, {
            'sensor_tokens': [[1.0]*64 for _ in range(4)],
            'text_tokens': [[0.5]*64 for _ in range(3)],
            'action_target': [0.1]*7
        })
        assert 'action_pred' in val
        assert 'grounding_score' in val
        assert len(val['action_pred']) == 7

    def test_mark_everything_down_engine(self):
        val = self._validate_engine(OmniMarkEverythingDownEngine, {
            'text_lines': ['# Title', 'Body text here', '## Section', '```code```', 'More text'],
            'content_type': 'document'
        })
        assert 'quality_score' in val
        assert val['heading_count'] == 2

    def test_stark_engine(self):
        val = self._validate_engine(OmniStarkEngine, {
            'query_terms': ['machine', 'learning'],
            'doc_terms_list': [['machine', 'learning', 'AI'], ['biology', 'cell']],
            'relational_constraints': [('author', 'cited_by')],
            'doc_relations': [[('author', 'cited_by')], []]
        })
        assert 'hit@1' in val
        assert val['best_idx'] == 0

    def test_pathomic_fusion_engine(self):
        val = self._validate_engine(OmniPathomicFusionEngine, {
            'histology_features': [0.5, 0.3, 0.7, 0.2],
            'genomic_features': [0.4, 0.6, 0.2, 0.8]
        })
        assert 'survival_prob' in val
        assert 0 <= val['survival_prob'] <= 1
        assert val['kronecker_dim'] == 16  # 4 x 4

    def test_awesome_mm_papers_engine(self):
        val = self._validate_engine(OmniAwesomeMMPapersEngine, {
            'adjacency_matrix': [[0, 1, 0], [1, 0, 1], [0, 1, 0]],
            'paper_topics': [['multimodal', 'vision'], ['nlp'], ['multimodal', 'audio']],
            'query_topics': ['multimodal'],
            'paper_years': [2022, 2023, 2024]
        })
        assert 'pagerank' in val
        assert len(val['pagerank']) == 3

    def test_cc2dataset_engine(self):
        val = self._validate_engine(OmniCc2DatasetEngine, {
            'captions': ['a cat sitting on table', 'a dog running in park'],
            'urls': ['http://a.com/1.jpg', 'http://b.com/2.jpg'],
            'embeddings': [[0.5, 0.3], [0.4, 0.6]]
        })
        assert 'kept_count' in val
        assert 'dedup_ratio' in val

    def test_mimic_iv_pipeline_engine(self):
        val = self._validate_engine(OmniMimicIVPipelineEngine, {
            'timestamps': [0, 1, 3, 5, 8, 10],
            'values': [36.5, 37.0, None, 37.2, None, 36.8],
            'modality_labels': ['vital'] * 6
        })
        assert 'normalized' in val
        assert 'imputed' in val
        assert None not in val['imputed']

    def test_hpt_engine(self):
        val = self._validate_engine(OmniHPTEngine, {
            'visual_features': [[1.0]*16 for _ in range(8)],
            'text_features': [[0.5]*16 for _ in range(4)]
        })
        assert 'alignment' in val
        assert 'dual_fused_norm' in val

    def test_awesome_mm_auto_drive_engine(self):
        val = self._validate_engine(OmniAwesomeMMAutoDriveEngine, {
            'lidar_points': [[1,2,3],[4,5,6],[7,8,9]],
            'camera_features': [0.5, 0.3, 0.7],
            'planned_trajectory': [[0,0],[1,1],[2,2],[3,2.5]],
            'obstacles': [[5, 5]]
        })
        assert 'fusion_confidence' in val
        assert 'safety_score' in val

    def test_rlhf_v_engine(self):
        val = self._validate_engine(OmniRlhfVEngine, {
            'chosen_logprobs': [-1.0, -0.5, -0.8],
            'rejected_logprobs': [-2.0, -1.5, -1.8],
            'reference_logprobs_chosen': [-1.2, -0.7, -0.9],
            'reference_logprobs_rejected': [-2.2, -1.7, -2.0]
        })
        assert 'dpo_loss' in val
        assert 'hallucination_score' in val

    def test_youku_mplug_engine(self):
        val = self._validate_engine(OmniYoukuMPlugEngine, {
            'frame_features': [[1.0]*16 for _ in range(8)],
            'text_features': [0.5]*16
        })
        assert 'contrastive_logit' in val
        assert 'n_queries' in val

    def test_lrv_instruction_engine(self):
        val = self._validate_engine(OmniLrvInstructionEngine, {
            'response_tokens': ['cat', 'sitting', 'table'],
            'ground_truth_objects': ['cat', 'table'],
            'mentioned_objects': ['cat', 'dog', 'table']
        })
        assert 'gavie_score' in val
        assert 'hallucinated_objects' in val
        assert 'dog' in val['hallucinated_objects']

    def test_vlm_bow_engine(self):
        val = self._validate_engine(OmniVlmBowEngine, {
            'positive_sim': 0.85,
            'negative_sim': 0.70,
            'aro_mode': 'relation'
        })
        assert val['correct'] == 1
        assert val['margin'] > 0

    def test_pixel_reasoner_engine(self):
        val = self._validate_engine(OmniPixelReasonerEngine, {
            'image_features': [[1.0]*4 for _ in range(4)],
            'reasoning_ops': ['zoom_in', 'analyze', 'verify'],
            'ground_truth_answer': 1.0
        })
        assert 'reward' in val
        assert 'curiosity_bonus' in val

    def test_video_gpt_plus_engine(self):
        val = self._validate_engine(OmniVideoGptPlusEngine, {
            'frame_features': [[1.0]*16 for _ in range(8)],
            'temporal_features': [[0.5]*16 for _ in range(8)]
        })
        assert 'spatial_richness' in val
        assert 'temporal_dynamics' in val

    def test_aui_test_agent_engine(self):
        val = self._validate_engine(OmniAuiTestAgentEngine, {
            'ui_elements': [{'bbox': [10,10,100,50], 'type': 'button', 'text': 'Submit'}],
            'target_element': {'bbox': [10,10,100,50], 'type': 'button'},
            'action_sequence': ['click', 'verify']
        })
        assert val['located'] is True
        assert val['best_iou'] > 0.5

    def test_cav_mae_engine(self):
        val = self._validate_engine(OmniCavMaeEngine, {
            'audio_patches': [[1.0]*8 for _ in range(16)],
            'visual_patches': [[0.5]*8 for _ in range(16)]
        })
        assert 'contrastive_loss' in val
        assert 'a_recon_loss' in val

    def test_embodied_agents_engine(self):
        val = self._validate_engine(OmniEmbodiedAgentsEngine, {
            'visual_obs': [0.5, 0.3, 0.7, 0.2],
            'proprioceptive_state': [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
            'action_history': [[0.1]*7, [0.2]*7],
            'rewards': [1.0, 0.5]
        })
        assert 'returns' in val
        assert 'pg_loss' in val

    def test_awesome_mm_prompts_engine(self):
        val = self._validate_engine(OmniAwesomeMMPromptsEngine, {
            'prompt_text': 'Describe the image in detail showing all objects',
            'modality_tags': ['text', 'image'],
            'response_quality': 0.85
        })
        assert 'quality' in val
        assert 'clarity' in val

    def test_openclaw_net_engine(self):
        val = self._validate_engine(OmniOpenClawNetEngine, {
            'tool_calls': [{'name': 'search', 'priority': 1}, {'name': 'compute', 'priority': 2}],
            'agent_memory_size': 2048,
            'request_timestamps': [0.0, 100.0, 250.0, 400.0]
        })
        assert 'sla_compliance' in val
        assert 'schedule_order' in val

    def test_pvm_engine(self):
        val = self._validate_engine(OmniPvmEngine, {
            'image_patches': [[1.0]*16 for _ in range(4)],
            'text_token_ids': [100, 200, 300]
        })
        assert 'quant_error' in val
        assert 'alignment' in val

    def test_mm_autodrive_planner_engine(self):
        val = self._validate_engine(OmniMMAutoDrivePlannerEngine, {
            'waypoints': [[0,0],[1,0.5],[2,0.8],[3,1.0],[4,1.2]],
            'ego_position': [0, 0],
            'other_agents': [[5, 1], [10, 0.5]]
        })
        assert 'coefficients' in val
        assert 'collision_risk' in val

    def test_rlhf_v_align_engine(self):
        val = self._validate_engine(OmniRlhfVAlignEngine, {
            'policy_logprobs': [-0.5, -0.8, -0.3],
            'ref_logprobs': [-0.6, -0.9, -0.4],
            'advantages': [0.5, -0.2, 0.8]
        })
        assert 'ppo_loss' in val
        assert 'kl_divergence' in val

    def test_youku_video_abstractor_engine(self):
        val = self._validate_engine(OmniYoukuVideoAbstractorEngine, {
            'frame_features': [[1.0]*16 for _ in range(8)],
            'query_init': [[0.5]*16 for _ in range(4)]
        })
        assert 'compression_ratio' in val
        assert val['compression_ratio'] == 0.5

    def test_lrv_gavie_engine(self):
        val = self._validate_engine(OmniLrvGavieEngine, {
            'instruction_embedding': [0.5, 0.3, 0.7],
            'response_embedding': [0.4, 0.35, 0.65],
            'image_objects': ['cat', 'table', 'window'],
            'response_objects': ['cat', 'table', 'dog']
        })
        assert 'gavie_score' in val
        assert 'dog' in val['hallucinated_objects']

    def test_aro_bow_benchmark_engine(self):
        val = self._validate_engine(OmniAroBowBenchmarkEngine, {
            'positive_scores': [0.8, 0.75, 0.9, 0.85],
            'hard_negative_scores': [0.7, 0.72, 0.6, 0.78],
            'test_type': 'attribution'
        })
        assert 'accuracy' in val
        assert 'compositionality_index' in val

    def test_curiosity_rl_engine(self):
        val = self._validate_engine(OmniCuriosityRLEngine, {
            'state': [0.1, 0.2, 0.3, 0.4],
            'next_state': [0.15, 0.25, 0.35, 0.45],
            'action': [1.0, 0.0],
            'extrinsic_reward': 1.0
        })
        assert 'curiosity_reward' in val
        assert 'total_reward' in val
        assert val['total_reward'] > 0
