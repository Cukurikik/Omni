# Omni Batch22 RAG+Rec Integration Test (Python)
def test_advanced_rag():
    from omni_advanced_rag_pipeline import corrective_rag, reciprocal_rank_fusion, adaptive_chunk
    result = corrective_rag("test", [{"score": 0.8}, {"score": 0.2}])
    assert result["action"] == "generate"
    fused = reciprocal_rank_fusion([["a","b","c"],["b","a","d"]])
    assert "a" in fused and "b" in fused
    chunks = adaptive_chunk("Hello world. This is a test. Another sentence. And more.", min_size=5, max_size=30)
    assert len(chunks) > 0
    print("[PASS] omni_advanced_rag_pipeline")

def test_alpharec_cf():
    from omni_alpharec_cf_engine import graph_conv, contrastive_loss, zero_shot_recommend
    node = [1.0, 0.0]; neighbors = [[0.0, 1.0], [0.5, 0.5]]
    result = graph_conv(node, neighbors)
    assert len(result) == 2
    loss = contrastive_loss([1,0], [0.9, 0.1], [[0, 1]], temp=0.1)
    assert loss > 0
    recs = zero_shot_recommend([1,0], [("i1", [0.9, 0.1]), ("i2", [0, 1])], top_k=1)
    assert recs[0][0] == "i1"
    print("[PASS] omni_alpharec_cf_engine")

def test_reclm():
    from omni_reclm_instruction_tuner import build_two_turn_prompt, ppo_reward
    prompt = build_two_turn_prompt(["item1", "item2"], "item3")
    assert "item1" in prompt
    r = ppo_reward(5, 10, 100)
    assert r > 0
    print("[PASS] omni_reclm_instruction_tuner")

if __name__ == "__main__":
    import sys; sys.path.insert(0, ".")
    test_advanced_rag(); test_alpharec_cf(); test_reclm()
    print("[ALL PASS] Batch 22 RAG+Rec tests")
