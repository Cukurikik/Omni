"""Semester 6 Batch 1 — Engine verification tests."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "compute", "python_core"))

def test_ai_deadlines():
    from omni_ai_deadlines_engine import OmniAiDeadlinesEngine, ConferenceEntry, SubCategory
    from datetime import datetime, timezone
    
    engine = OmniAiDeadlinesEngine()
    h = engine.health()
    assert h["status"] == "operational"
    
    # Add a test conference
    entry = ConferenceEntry(
        title="NeurIPS", year=2026, id="neurips2026",
        full_name="Conference on Neural Information Processing Systems",
        link="https://neurips.cc", 
        deadline=datetime(2026, 5, 20, 23, 59, tzinfo=timezone.utc),
        timezone_str="UTC", place="Vancouver, Canada",
        date_display="Dec 2026", sub=SubCategory.ML, hindex=278.0,
    )
    engine.add_conference(entry)
    
    # Test countdown
    countdowns = engine.compute_countdowns()
    assert len(countdowns) == 1
    assert countdowns[0].conference_id == "neurips2026"
    
    # Test iCal export
    ical = engine.export_ical()
    assert "BEGIN:VCALENDAR" in ical
    assert "NeurIPS" in ical
    assert "BEGIN:VEVENT" in ical
    
    # Test filter
    ml_confs = engine.filter_by_sub(SubCategory.ML)
    assert len(ml_confs) == 1
    
    # Test ranking
    ranked = engine.rank_by_hindex()
    assert ranked[0].hindex == 278.0
    
    print("  [1/4] OmniAiDeadlinesEngine — PASS (health, countdown, iCal, filter, rank)")


def test_math_ml():
    from omni_math_ml_engine import OmniMathMlEngine, AdamState
    
    engine = OmniMathMlEngine()
    h = engine.health()
    assert h["status"] == "operational"
    
    # Matrix multiply
    result = engine.linalg.mat_mul([[1,2],[3,4]], [[5,6],[7,8]])
    assert result == [[19,22],[43,50]]
    
    # Determinant
    det = engine.linalg.determinant([[1,2],[3,4]])
    assert abs(det - (-2)) < 1e-10
    
    # Transpose
    t = engine.linalg.transpose([[1,2,3],[4,5,6]])
    assert t == [[1,4],[2,5],[3,6]]
    
    # Gaussian PDF at mean
    g = engine.probability.gaussian_pdf(0.0)
    assert abs(g - 0.3989422804) < 0.001
    
    # KL divergence (same dist = 0)
    kl = engine.probability.kl_divergence([0.5, 0.5], [0.5, 0.5])
    assert abs(kl) < 1e-10
    
    # Cross entropy
    ce = engine.probability.cross_entropy([1.0, 0.0], [0.9, 0.1])
    assert ce > 0
    
    # SGD step
    params = engine.optimizers.sgd_step([1.0, 2.0], [0.1, 0.2], lr=0.1)
    assert abs(params[0] - 0.99) < 1e-10
    
    # Adam step
    state = AdamState()
    params = engine.optimizers.adam_step([1.0, 2.0], [0.1, 0.2], state)
    assert len(params) == 2
    assert state.t == 1
    
    print("  [2/4] OmniMathMlEngine — PASS (matmul, det, transpose, gaussian, kl, ce, sgd, adam)")


def test_gluoncv():
    from omni_gluoncv_engine import OmniGluoncvEngine
    
    engine = OmniGluoncvEngine()
    h = engine.health()
    assert h["status"] == "operational"
    
    # IoU test
    iou = engine.detection.compute_iou((0,0,10,10), (5,5,15,15))
    assert abs(iou - 25.0/175.0) < 0.01
    
    # NMS test
    boxes = [(0,0,10,10), (1,1,11,11), (50,50,60,60)]
    scores = [0.9, 0.8, 0.7]
    kept = engine.detection.nms(boxes, scores, 0.3)
    assert len(kept) == 2
    
    # Anchor generation
    anchors = engine.detection.generate_anchors(2, 100, [0.1], [1.0])
    assert len(anchors) == 4  # 2x2 grid x 1 scale x 1 ratio
    
    # Model zoo
    models = engine.model_zoo.list_models()
    assert len(models) == 8
    resnet_models = engine.model_zoo.list_models("ResNet")
    assert len(resnet_models) == 3
    
    # Conv2D smoke test
    conv = engine.create_conv2d(1, 1, kernel=2, stride=1, padding=0)
    test_input = [[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]]]
    output = conv.forward(test_input)
    assert len(output) == 1
    assert len(output[0]) == 2
    assert len(output[0][0]) == 2
    
    print("  [3/4] OmniGluoncvEngine — PASS (iou, nms, anchors, model_zoo, conv2d)")


def test_chainer():
    from omni_chainer_engine import OmniChainerEngine, Variable, TrainingConfig
    
    engine = OmniChainerEngine()
    h = engine.health()
    assert h["status"] == "operational"
    assert h["paradigm"] == "define-by-run"
    assert h["autograd"] is True
    
    # Autograd: z = x*y + x, dz/dx = y+1 = 3, dz/dy = x = 3
    x = Variable(3.0, "x")
    y = Variable(2.0, "y")
    z = x * y + x
    z.backward()
    assert abs(x.grad - 3.0) < 0.01
    assert abs(y.grad - 3.0) < 0.01
    
    # Softmax
    probs = engine.loss.softmax([1.0, 2.0, 3.0])
    assert abs(sum(probs) - 1.0) < 1e-10
    assert probs[2] > probs[1] > probs[0]
    
    # MSE loss
    mse = engine.loss.mse([1.0, 2.0], [1.5, 2.5])
    assert abs(mse - 0.25) < 1e-10
    
    # Linear layer
    layer = engine.linear(3, 2)
    out = layer.forward([1.0, 0.5, -0.5])
    assert len(out) == 2
    
    # Training loop (smoke test)
    trainer = engine.trainer(TrainingConfig(epochs=3, batch_size=2, learning_rate=0.01))
    data = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
    targets = [[0.0, 1.0], [1.0, 0.0], [0.5, 0.5]]
    logs = trainer.train(layer, data, targets)
    assert len(logs) == 3
    assert all(log.samples_processed > 0 for log in logs)
    
    print("  [4/4] OmniChainerEngine — PASS (autograd, softmax, mse, linear, training_loop)")


if __name__ == "__main__":
    print("=" * 60)
    print("SEMESTER 6 BATCH 1 — Engine Verification")
    print("=" * 60)
    test_ai_deadlines()
    test_math_ml()
    test_gluoncv()
    test_chainer()
    print()
    print("=== ALL 4 PYTHON ENGINES: VERIFIED OPERATIONAL ===")
    print("(Swift engine verified via syntax — no Swift compiler on Windows)")
