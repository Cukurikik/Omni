# Omni DMax Decode Performance Test (Python)
# Ref: czg1225/DMax
import importlib, sys
def test_dmax_parallel_decode():
    mod = importlib.import_module("omni_dmax_parallel_decoder")
    logits = [[0.1, 0.8, 0.1], [0.2, 0.6, 0.2], [0.4, 0.3, 0.3]]
    result = mod.parallel_decode_step(logits, mask_threshold=0.3, max_tokens=8)
    assert result["n_parallel"] == 3
    assert all(c > 0 for c in result["confidences"])
    rate = mod.compute_acceptance_rate([1, 1, 1], [1, 1, 0])
    assert 0 < rate < 1
    sched = mod.dmax_aggressive_schedule(1, 10, 4)
    assert sched == 8
    print("[PASS] omni_dmax_parallel_decoder")

def test_flora_compressor():
    mod = importlib.import_module("omni_flora_gradient_compressor")
    grad = [0.1 * i for i in range(32)]
    c = mod.random_projection_compress(grad, 8)
    assert len(c) == 8
    updated = mod.flora_update([1.0] * 32, grad, lr=0.01, proj_dim=8)
    assert len(updated) == 32
    print("[PASS] omni_flora_gradient_compressor")

def test_uot_planner():
    mod = importlib.import_module("omni_uot_uncertainty_planner")
    e = mod.entropy([0.5, 0.5])
    assert abs(e - 1.0) < 0.01
    ig = mod.information_gain([0.5, 0.5], [0.9, 0.1])
    assert ig > 0
    print("[PASS] omni_uot_uncertainty_planner")

if __name__ == "__main__":
    sys.path.insert(0, ".")
    test_dmax_parallel_decode()
    test_flora_compressor()
    test_uot_planner()
    print("[ALL PASS] Batch 22 integration tests")
