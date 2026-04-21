"""
OMNI Semester 9 — Batch 2 Integration Test Suite
===================================================
Comprehensive integration tests validating all 9 engines from
Semester 9 Batch 2 for structural integrity, monadic compliance,
and production-grade operational readiness.

Engines Under Test:
1. OmniArgoWorkflowEngine
2. OmniSpacyCourseEngine
3. OmniMetarankEngine
4. OmniHuggingFaceJsEngine
5. OmniTorchioMedicalEngine
6. OmniAwesomeChatgptEngine
7. OmniOtermEngine
8. OmniModalActiveLearningEngine
9. OmniObjectronEngine
"""

from __future__ import annotations

import sys
import traceback
from dataclasses import dataclass
from typing import Any, List, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Test Framework
# ---------------------------------------------------------------------------

@dataclass
class TestResult:
    """Result of a single test case."""
    name: str
    passed: bool
    detail: str = ""


class TestSuite:
    """Lightweight test runner."""

    def __init__(self) -> None:
        """Initialise test suite."""
        self.results: List[TestResult] = []

    def assert_true(self, name: str, condition: bool, detail: str = "") -> None:
        """Assert condition is True."""
        self.results.append(TestResult(name, condition, detail))

    def assert_ok(self, name: str, result: Any) -> None:
        """Assert result is an Ok monad."""
        from omni_argo_workflow_engine import Ok
        is_ok = type(result).__name__ == "Ok" or isinstance(result, Ok)
        self.results.append(TestResult(
            name, is_ok,
            f"Expected Ok, got {type(result).__name__}: {result}" if not is_ok else "",
        ))

    def assert_err(self, name: str, result: Any) -> None:
        """Assert result is an Err monad."""
        from omni_argo_workflow_engine import Err
        is_err = type(result).__name__ == "Err" or isinstance(result, Err)
        self.results.append(TestResult(
            name, is_err,
            f"Expected Err, got {type(result).__name__}" if not is_err else "",
        ))

    def summary(self) -> str:
        """Return formatted test summary."""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        lines = [f"\n{'='*70}", f"SEMESTER 9 -- BATCH 2 INTEGRATION TESTS",
                 f"{'='*70}"]
        for r in self.results:
            status = "[PASS]" if r.passed else "[FAIL]"
            lines.append(f"  {status} | {r.name}")
            if r.detail and not r.passed:
                lines.append(f"         -> {r.detail}")
        lines.append(f"{'='*70}")
        lines.append(f"Results: {passed}/{total} passed")
        if passed == total:
            lines.append("[OK] ALL TESTS PASSED -- BATCH 2 OPERATIONAL")
        else:
            lines.append(f"[ERR] {total - passed} TEST(S) FAILED")
        lines.append(f"{'='*70}\n")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Add parent path
# ---------------------------------------------------------------------------
sys.path.insert(0, ".")

suite = TestSuite()

# ===================================================================
# TEST GROUP 1: OmniArgoWorkflowEngine
# ===================================================================
try:
    from omni_argo_workflow_engine import (
        OmniArgoWorkflowEngine, Ok, Err, RolloutStrategy,
    )

    engine = OmniArgoWorkflowEngine()

    # T1.1 — Diagnostics
    diag = engine.diagnostics()
    suite.assert_true("Argo: diagnostics returns dict",
                      isinstance(diag, dict) and diag.get("status") == "operational")

    # T1.2 — Register and run workflow
    def step_a(inputs, outputs):
        return Ok(inputs.get("val", 0) + 10)

    def step_b(inputs, outputs):
        return Ok(outputs.get("a", 0) * 2)

    suite.assert_ok("Argo: register step a", engine.register_step("a", step_a))
    suite.assert_ok("Argo: register step b", engine.register_step("b", step_b, deps=["a"]))
    result = engine.run_workflow({"val": 5})
    suite.assert_ok("Argo: DAG execution", result)
    suite.assert_true("Argo: correct DAG output",
                      isinstance(result, Ok) and result.value.get("b") == 30)

    # T1.3 — Duplicate step
    suite.assert_err("Argo: duplicate step rejected", engine.register_step("a", step_a))

    # T1.4 — GitOps application
    suite.assert_ok("Argo: create app", engine.create_application("web", "https://github.com/user/repo"))
    suite.assert_ok("Argo: sync app", engine.sync_application("web"))
    suite.assert_err("Argo: sync unknown app", engine.sync_application("nonexistent"))

    # T1.5 — Rollout
    suite.assert_ok("Argo: create rollout", engine.create_rollout("canary-v1"))
    suite.assert_ok("Argo: promote rollout", engine.promote_rollout("canary-v1"))

except Exception as exc:
    suite.assert_true(f"Argo: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 2: OmniSpacyCourseEngine
# ===================================================================
try:
    from omni_spacy_course_engine import OmniSpacyCourseEngine

    engine = OmniSpacyCourseEngine()

    # T2.1 — Diagnostics
    diag = engine.diagnostics()
    suite.assert_true("spaCy: diagnostics operational",
                      diag.get("status") == "operational")

    # T2.2 — Tokenization
    tok_res = engine.tokenize("Google announced new features in Berlin.")
    suite.assert_ok("spaCy: tokenize", tok_res)
    suite.assert_true("spaCy: tokens are list",
                      isinstance(tok_res.value, list) and len(tok_res.value) > 0)

    # T2.3 — NER
    ner_res = engine.find_entities("Google announced new features in Berlin.")
    suite.assert_ok("spaCy: find_entities", ner_res)
    labels = [e["label"] for e in ner_res.value]
    suite.assert_true("spaCy: ORG entity found", "ORG" in labels)

    # T2.4 — Empty input
    suite.assert_err("spaCy: empty text error", engine.tokenize(""))

    # T2.5 — Pattern matching
    pat_res = engine.match_pattern(
        "Google is great", "adj_noun",
        [{"POS": "PROPN"}, {"POS": "AUX"}],
    )
    suite.assert_ok("spaCy: pattern match", pat_res)

except Exception as exc:
    suite.assert_true(f"spaCy: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 3: OmniMetarankEngine
# ===================================================================
try:
    from omni_metarank_engine import OmniMetarankEngine, RankingItem

    engine = OmniMetarankEngine()

    # T3.1 — Diagnostics
    diag = engine.diagnostics()
    suite.assert_true("Metarank: diagnostics operational",
                      diag.get("status") == "operational")

    # T3.2 — Feature registration
    suite.assert_ok("Metarank: register price", engine.register_feature("price"))
    suite.assert_ok("Metarank: register clicks", engine.register_feature("clicks"))
    suite.assert_err("Metarank: dup feature", engine.register_feature("price"))

    # T3.3 — Training
    pos = [RankingItem("a", {"price": 100, "clicks": 50}, 1.0)]
    neg = [RankingItem("b", {"price": 20, "clicks": 5}, 0.0)]
    suite.assert_ok("Metarank: train pairwise", engine.train(pos, neg))

    # T3.4 — Ranking
    items = [
        RankingItem("x", {"price": 80, "clicks": 40}),
        RankingItem("y", {"price": 30, "clicks": 10}),
    ]
    rank_res = engine.rank(items)
    suite.assert_ok("Metarank: rank items", rank_res)

    # T3.5 — Event ingestion
    suite.assert_ok("Metarank: ingest event", engine.ingest_event("click", "u1", "x"))

    # T3.6 — Evaluation
    eval_items = [
        RankingItem("x", {"price": 80, "clicks": 40}, 1.0),
        RankingItem("y", {"price": 30, "clicks": 10}, 0.0),
    ]
    eval_res = engine.evaluate(eval_items, k=2)
    suite.assert_ok("Metarank: evaluate NDCG/MRR", eval_res)

except Exception as exc:
    suite.assert_true(f"Metarank: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 4: OmniHuggingFaceJsEngine
# ===================================================================
try:
    from omni_huggingface_js_engine import OmniHuggingFaceJsEngine

    engine = OmniHuggingFaceJsEngine()

    # T4.1 — Diagnostics
    diag = engine.diagnostics()
    suite.assert_true("HF-JS: diagnostics operational",
                      diag.get("status") == "operational")

    # T4.2 — Search models
    search_res = engine.search_models(query="bert")
    suite.assert_ok("HF-JS: search models", search_res)
    suite.assert_true("HF-JS: found bert results",
                      len(search_res.value) > 0)

    # T4.3 — Inference
    infer_res = engine.run_inference("gpt2", "Hello world")
    suite.assert_ok("HF-JS: run inference", infer_res)

    # T4.4 — Unknown provider
    suite.assert_err("HF-JS: unknown provider", engine.run_inference("gpt2", "test", "invalid"))

    # T4.5 — Tokenizer encode/decode
    enc_res = engine.encode_text("hello")
    suite.assert_ok("HF-JS: encode text", enc_res)
    dec_res = engine.decode_ids(enc_res.value)
    suite.assert_ok("HF-JS: decode ids", dec_res)
    suite.assert_true("HF-JS: roundtrip decode", dec_res.value == "hello")

    # T4.6 — Empty input error
    suite.assert_err("HF-JS: empty encode error", engine.encode_text(""))

except Exception as exc:
    suite.assert_true(f"HF-JS: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 5: OmniTorchioMedicalEngine
# ===================================================================
try:
    from omni_torchio_medical_engine import OmniTorchioMedicalEngine

    engine = OmniTorchioMedicalEngine()

    # T5.1 — Diagnostics
    diag = engine.diagnostics()
    suite.assert_true("TorchIO: diagnostics operational",
                      diag.get("status") == "operational")

    # T5.2 — Create image
    data = np.random.randn(1, 16, 32, 32).astype(np.float32)
    img_res = engine.create_image(data)
    suite.assert_ok("TorchIO: create image", img_res)

    # T5.3 — Wrong dimensions
    bad_data = np.random.randn(16, 32).astype(np.float32)
    suite.assert_err("TorchIO: reject 2D data", engine.create_image(bad_data))

    # T5.4 — Apply rescale
    img = img_res.value
    rescale_res = engine.apply_transform(img, "rescale")
    suite.assert_ok("TorchIO: rescale transform", rescale_res)
    suite.assert_true("TorchIO: rescaled range",
                      rescale_res.value.data.min() >= -0.01 and rescale_res.value.data.max() <= 1.01)

    # T5.5 — Z-normalisation
    znorm_res = engine.apply_transform(img, "znorm")
    suite.assert_ok("TorchIO: z-norm transform", znorm_res)

    # T5.6 — Pipeline
    pipe_res = engine.build_pipeline([("rescale", {}), ("znorm", {})])
    suite.assert_ok("TorchIO: build pipeline", pipe_res)

    # T5.7 — Patch extraction
    patch_res = engine.extract_patches(img, (8, 16, 16))
    suite.assert_ok("TorchIO: extract patches", patch_res)
    suite.assert_true("TorchIO: patches created", len(patch_res.value) > 0)

    # T5.8 — Statistics
    stats_res = engine.compute_statistics(img)
    suite.assert_ok("TorchIO: compute stats", stats_res)

    # T5.9 — Unknown transform
    suite.assert_err("TorchIO: unknown transform", engine.apply_transform(img, "nonexistent"))

except Exception as exc:
    suite.assert_true(f"TorchIO: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 6: OmniAwesomeChatgptEngine
# ===================================================================
try:
    from omni_awesome_chatgpt_engine import OmniAwesomeChatgptEngine

    engine = OmniAwesomeChatgptEngine()

    # T6.1 — Diagnostics
    diag = engine.diagnostics()
    suite.assert_true("ChatGPT: diagnostics operational",
                      diag.get("status") == "operational")

    # T6.2 — Search resources
    search_res = engine.search_resources(query="openai")
    suite.assert_ok("ChatGPT: search resources", search_res)
    suite.assert_true("ChatGPT: found resources", len(search_res.value) > 0)

    # T6.3 — Category filter
    sdk_res = engine.search_resources(category="sdk-python")
    suite.assert_ok("ChatGPT: category filter", sdk_res)

    # T6.4 — Unknown category
    suite.assert_err("ChatGPT: unknown category", engine.search_resources(category="invalid"))

    # T6.5 — Render prompt
    render_res = engine.render_prompt("explain", topic="quantum computing",
                                        audience="5 year old")
    suite.assert_ok("ChatGPT: render prompt", render_res)
    suite.assert_true("ChatGPT: prompt has content",
                      "quantum computing" in render_res.value)

    # T6.6 — Missing params
    missing_res = engine.render_prompt("explain", topic="AI")
    suite.assert_err("ChatGPT: missing prompt param", missing_res)

    # T6.7 — List templates
    list_res = engine.list_prompt_templates()
    suite.assert_ok("ChatGPT: list templates", list_res)

except Exception as exc:
    suite.assert_true(f"ChatGPT: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 7: OmniOtermEngine
# ===================================================================
try:
    from omni_oterm_engine import OmniOtermEngine

    engine = OmniOtermEngine()

    # T7.1 — Diagnostics
    diag = engine.diagnostics()
    suite.assert_true("Oterm: diagnostics operational",
                      diag.get("status") == "operational")

    # T7.2 — List models
    models_res = engine.list_models()
    suite.assert_ok("Oterm: list models", models_res)
    suite.assert_true("Oterm: models available", len(models_res.value) > 0)

    # T7.3 — Create session
    sess_res = engine.create_session("llama3.1:8b", "You are a coding assistant.")
    suite.assert_ok("Oterm: create session", sess_res)
    session_id = sess_res.value["session_id"]

    # T7.4 — Session with unknown model
    suite.assert_err("Oterm: unknown model session",
                     engine.create_session("nonexistent-model:99b"))

    # T7.5 — Send message
    msg_res = engine.send_message(session_id, "Explain recursion.")
    suite.assert_ok("Oterm: send message", msg_res)
    suite.assert_true("Oterm: response has content",
                      len(msg_res.value["content"]) > 0)

    # T7.6 — Empty message
    suite.assert_err("Oterm: empty message", engine.send_message(session_id, ""))

    # T7.7 — List sessions
    sessions_res = engine.list_sessions()
    suite.assert_ok("Oterm: list sessions", sessions_res)

    # T7.8 — Pull model
    suite.assert_ok("Oterm: pull new model", engine.pull_model("deepseek-coder:6.7b"))

except Exception as exc:
    suite.assert_true(f"Oterm: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 8: OmniModalActiveLearningEngine
# ===================================================================
try:
    from omni_modal_active_learning_engine import OmniModalActiveLearningEngine

    engine = OmniModalActiveLearningEngine()

    # T8.1 — Diagnostics
    diag = engine.diagnostics()
    suite.assert_true("modAL: diagnostics operational",
                      diag.get("status") == "operational")

    # T8.2 — Create learner
    suite.assert_ok("modAL: create learner",
                    engine.create_learner("clf1", n_features=4, n_classes=3))
    suite.assert_err("modAL: dup learner", engine.create_learner("clf1", 4))

    # T8.3 — Unknown strategy
    suite.assert_err("modAL: unknown strategy",
                     engine.create_learner("bad", 4, strategy="invalid"))

    # T8.4 — Train
    X = np.random.randn(30, 4)
    y = np.array([0]*10 + [1]*10 + [2]*10)
    teach_res = engine.teach("clf1", X, y)
    suite.assert_ok("modAL: teach learner", teach_res)

    # T8.5 — Query
    X_pool = np.random.randn(20, 4)
    query_res = engine.query("clf1", X_pool, n_instances=3)
    suite.assert_ok("modAL: query pool", query_res)
    suite.assert_true("modAL: 3 indices returned", len(query_res.value) == 3)

    # T8.6 — Evaluate
    X_test = np.random.randn(15, 4)
    y_test = np.array([0]*5 + [1]*5 + [2]*5)
    eval_res = engine.evaluate("clf1", X_test, y_test)
    suite.assert_ok("modAL: evaluate accuracy", eval_res)

    # T8.7 — Committee
    suite.assert_ok("modAL: create committee",
                    engine.create_committee("com1", n_features=4, n_classes=3))

    # T8.8 — Query unfitted learner
    engine.create_learner("unfitted", n_features=2)
    suite.assert_err("modAL: query unfitted", engine.query("unfitted", np.zeros((5, 2))))

except Exception as exc:
    suite.assert_true(f"modAL: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# TEST GROUP 9: OmniObjectronEngine
# ===================================================================
try:
    from omni_objectron_engine import OmniObjectronEngine

    engine = OmniObjectronEngine()

    # T9.1 — Diagnostics
    diag = engine.diagnostics()
    suite.assert_true("Objectron: diagnostics operational",
                      diag.get("status") == "operational")

    # T9.2 — Create bounding box
    bbox_res = engine.create_bounding_box([0.0, 0.0, 5.0], [0.3, 0.5, 0.3], "cup")
    suite.assert_ok("Objectron: create bbox", bbox_res)

    # T9.3 — Invalid category
    suite.assert_err("Objectron: invalid category",
                     engine.create_bounding_box([0, 0, 0], [1, 1, 1], "spaceship"))

    # T9.4 — Wrong dims
    suite.assert_err("Objectron: wrong center dims",
                     engine.create_bounding_box([0, 0], [1, 1, 1]))

    # T9.5 — IoU computation
    box_a_res = engine.create_bounding_box([0, 0, 5], [1, 1, 1], "cup")
    box_b_res = engine.create_bounding_box([0.5, 0, 5], [1, 1, 1], "cup")
    iou_res = engine.compute_iou(box_a_res.value, box_b_res.value)
    suite.assert_ok("Objectron: compute IoU", iou_res)
    suite.assert_true("Objectron: IoU > 0", iou_res.value["iou"] > 0)

    # T9.6 — Projection
    proj_res = engine.project_to_2d(bbox_res.value)
    suite.assert_ok("Objectron: project to 2D", proj_res)
    suite.assert_true("Objectron: 8 projected corners",
                      len(proj_res.value["corners_2d"]) == 8)

    # T9.7 — Evaluation
    preds = [box_a_res.value]
    gts = [box_b_res.value]
    ap_res = engine.evaluate_detections(preds, gts, iou_threshold=0.1)
    suite.assert_ok("Objectron: average precision", ap_res)

    # T9.8 — Frame annotation
    suite.assert_ok("Objectron: add frame annotation",
                    engine.add_frame_annotation(0, 0.0, [bbox_res.value]))

except Exception as exc:
    suite.assert_true(f"Objectron: IMPORT/INIT ERROR: {exc}", False, traceback.format_exc())

# ===================================================================
# PRINT RESULTS
# ===================================================================
print(suite.summary())
sys.exit(0 if all(r.passed for r in suite.results) else 1)
