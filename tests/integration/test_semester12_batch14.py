import pytest
from src.compute.python_core.omni_vis_cpm_engine import OmniVisCpmEngine
from src.compute.python_core.omni_one_peace_engine import OmniOnePeaceEngine
from src.compute.python_core.omni_clip4clip_engine import OmniClip4clipEngine
from src.compute.python_core.omni_point_llm_engine import OmniPointLlmEngine
from src.compute.python_core.omni_awesome_mcot_engine import OmniAwesomeMcotEngine
from src.compute.python_core.omni_mova_engine import OmniMovaEngine
from src.compute.python_core.omni_vectordb_recipes_engine import OmniVectordbRecipesEngine
from src.compute.python_core.omni_top_cvpr_2025_papers_engine import OmniTopCvpr2025PapersEngine
from src.compute.python_core.omni_rag_time_engine import OmniRagTimeEngine
from src.compute.python_core.omni_papermage_engine import OmniPapermageEngine
from src.compute.python_core.omni_autoregressive_models_in_vision_survey_engine import OmniAutoregressiveModelsInVisionSurveyEngine
from src.compute.python_core.omni_contrastors_engine import OmniContrastorsEngine
from src.compute.python_core.omni_lmms_engine_engine import OmniLmmsEngineEngine
from src.compute.python_core.omni_multimodal_and_large_language_models_engine import OmniMultimodalAndLargeLanguageModelsEngine
from src.compute.python_core.omni_paddle_mix_engine import OmniPaddleMixEngine
from src.compute.python_core.omni_instruct_ir_engine import OmniInstructIrEngine
from src.compute.python_core.omni_neo_engine import OmniNeoEngine
from src.compute.python_core.omni_ohmycaptcha_engine import OmniOhmycaptchaEngine
from src.compute.python_core.omni_pluralistic_inpainting_engine import OmniPluralisticInpaintingEngine

class TestSemester12Batch14:

    def test_omni_vis_cpm_engine(self):
        engine = OmniVisCpmEngine()
        result = engine.compute_cross_attention(queries=[[1.0, 0.0], [0.0, 1.0]], keys=[[1.0, 0.0], [0.0, 1.0]])
        assert result.is_ok()
        assert "attention_scores" in result.unwrap()["data"]

    def test_omni_one_peace_engine(self):
        engine = OmniOnePeaceEngine()
        result = engine.compute_triplet_contrastive_loss(anchor=[1.0, 1.0], positive=[1.0, 1.0], negative=[-1.0, -1.0])
        assert result.is_ok()
        assert result.unwrap()["data"]["triplet_loss"] == 0.0

    def test_omni_clip4clip_engine(self):
        engine = OmniClip4clipEngine()
        result = engine.evaluate_video_text_similarity(frame_embs=[[1.0, 0.0], [1.0, 0.5]], text_emb=[1.0, 0.0])
        assert result.is_ok()
        assert result.unwrap()["data"]["video_similarity"] > 0

    def test_omni_point_llm_engine(self):
        engine = OmniPointLlmEngine()
        result = engine.compute_chamfer_distance(pc1=[(0.0, 0.0, 0.0)], pc2=[(1.0, 1.0, 1.0)])
        assert result.is_ok()

    def test_omni_awesome_mcot_engine(self):
        engine = OmniAwesomeMcotEngine()
        result = engine.evaluate_reasoning_tree(adjacency_list={"A": ["B", "C"], "B": ["D"]}, start_node="A")
        assert result.is_ok()
        assert result.unwrap()["data"]["max_reasoning_depth"] == 2

    def test_omni_mova_engine(self):
        engine = OmniMovaEngine()
        result = engine.calculate_tempo_alignment(video_beats=[1.0, 2.0, 3.0], audio_beats=[1.1, 2.1, 2.9])
        assert result.is_ok()

    def test_omni_vectordb_recipes_engine(self):
        engine = OmniVectordbRecipesEngine()
        result = engine.query_vector_l2_scan(query=[0.0, 0.0], database=[[1.0, 1.0], [0.0, 0.1]], top_k=1)
        assert result.is_ok()
        assert result.unwrap()["data"]["top_indices"][0] == 1

    def test_omni_top_cvpr_2025_papers_engine(self):
        engine = OmniTopCvpr2025PapersEngine()
        result = engine.compute_citation_influence(edges=[(0, 1), (1, 2)], num_papers=3)
        assert result.is_ok()

    def test_omni_rag_time_engine(self):
        engine = OmniRagTimeEngine()
        result = engine.compute_bm25_score(doc_lengths=[100, 200], avg_dl=150.0, term_freq=5, doc_count=1000, doc_freq=50)
        assert result.is_ok()

    def test_omni_papermage_engine(self):
        engine = OmniPapermageEngine()
        result = engine.compute_iou_matrix(boxes=[(0,0,10,10), (5,5,15,15)])
        assert result.is_ok()

    def test_omni_autoregressive_models_in_vision_survey_engine(self):
        engine = OmniAutoregressiveModelsInVisionSurveyEngine()
        result = engine.compute_cross_entropy_perplexity(logits=[[1.0, -1.0, -2.0]], target_indices=[0])
        assert result.is_ok()

    def test_omni_contrastors_engine(self):
        engine = OmniContrastorsEngine()
        result = engine.calculate_infonce_loss(sim_matrix=[[1.0, 0.1], [0.1, 1.0]])
        assert result.is_ok()

    def test_omni_lmms_engine_engine(self):
        engine = OmniLmmsEngineEngine()
        result = engine.accumulate_virtual_gradients(micro_batch_grads=[[0.1, 0.1], [0.2, 0.2]])
        assert result.is_ok()

    def test_omni_multimodal_and_large_language_models_engine(self):
        engine = OmniMultimodalAndLargeLanguageModelsEngine()
        result = engine.project_visual_to_textual(visual_emb=[1.0, 0.0], projection_matrix=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
        assert result.is_ok()
        
    def test_omni_paddle_mix_engine(self):
        engine = OmniPaddleMixEngine()
        result = engine.compute_linear_variance_schedule(timesteps=10)
        assert result.is_ok()

    def test_omni_instruct_ir_engine(self):
        engine = OmniInstructIrEngine()
        result = engine.calculate_psnr_metric(mse_distortion=0.5)
        assert result.is_ok()

    def test_omni_neo_engine(self):
        engine = OmniNeoEngine()
        result = engine.calculate_fusion_entropy(fusion_activations=[0.1, 0.9])
        assert result.is_ok()

    def test_omni_ohmycaptcha_engine(self):
        engine = OmniOhmycaptchaEngine()
        result = engine.solve_jigsaw_sliding_window(background_vector=[0.0, 0.1, 1.0, 1.0, 0.1], puzzle_piece=[1.0, 1.0])
        assert result.is_ok()

    def test_omni_pluralistic_inpainting_engine(self):
        engine = OmniPluralisticInpaintingEngine()
        result = engine.compute_boundary_gradient_loss(source_boundary=[0.0, 0.5, 1.0], target_boundary=[0.0, 0.4, 0.9])
        assert result.is_ok()
