# Omni Batch 23 Integration Test
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'compute', 'python_core'))

def test_batch23():
    from omni_simplyretrieve_rcg_engine import build_knowledge_base, rcg_retrieve, retrieval_tuning_score
    docs = [{"id": "d1", "text": "neural network deep learning"}, {"id": "d2", "text": "database query sql"}]
    kb = build_knowledge_base(docs)
    assert kb["n_docs"] == 2
    results = rcg_retrieve("neural learning", kb, docs)
    assert len(results) >= 1

    from omni_flask_evaluator import evaluate_response, SKILLS
    scores = {s: 4.0 for s in SKILLS[:6]}
    result = evaluate_response(scores)
    assert result["overall"] == 4.0

    from omni_fusionbench_merger import task_arithmetic_merge, dare_prune
    base = [1.0, 2.0, 3.0]
    merged = task_arithmetic_merge(base, [[1.5, 2.5, 3.5]], 0.5)
    assert len(merged) == 3
    pruned = dare_prune([0.1, 0.2, 0.3], 0.5)
    assert len(pruned) == 3

    from omni_qgalore_optimizer import int4_quantize, int4_dequantize, layer_adaptive_rank
    q = int4_quantize([0.1, 0.5, 0.9])
    assert len(q["quantized"]) == 3
    ranks = layer_adaptive_rank([1.0, 2.0, 3.0], 32, 64)
    assert sum(ranks) <= 64

    from omni_lion_distillation import imitation_loss, discriminate_hard_instructions
    loss = imitation_loss([1.0, 2.0], [1.5, 2.5])
    assert loss >= 0
    hard = discriminate_hard_instructions([0.5, 0.6], [0.9, 0.7], 0.2)
    assert isinstance(hard, list)

    from omni_kopa_kg_adapter import structural_embedding, kgc_score
    emb = structural_embedding(1, [2, 3], 16)
    assert len(emb) == 16
    s = kgc_score([0.1]*4, [0.2]*4, [0.3]*4)
    assert isinstance(s, float)

    from omni_iepile_extraction import build_ner_instruction, evaluate_ie
    inst = build_ner_instruction("Hello world", ["PERSON"])
    assert inst["task"] == "NER"

    print("[ALL PASS] Batch 23 core engines verified")

if __name__ == "__main__":
    test_batch23()
