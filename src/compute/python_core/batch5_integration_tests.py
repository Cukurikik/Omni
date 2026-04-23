# -*- coding: utf-8 -*-
"""
Batch 5 (Semester 7) — Comprehensive Integration Test Suite
50+ tests across all 5 Batch 5 engines.
"""
import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(__file__))

_PASS = 0
_FAIL = 0
_ERRORS = []


def _assert(condition, test_name, detail=""):
    global _PASS, _FAIL
    if condition:
        _PASS += 1
    else:
        _FAIL += 1
        _ERRORS.append(f"FAIL: {test_name} -- {detail}")


def _run(fn, test_name):
    global _FAIL
    try:
        fn()
    except Exception as exc:
        _FAIL += 1
        _ERRORS.append(f"ERROR: {test_name} -- {traceback.format_exc()}")


# ======================================================================
# ENGINE 1: OmniPennyLaneQMLEngine (10 tests)
# ======================================================================

def test_pennylane_diagnostics():
    from system.omni_pennylane_qml_engine import OmniPennyLaneQMLEngine
    e = OmniPennyLaneQMLEngine()
    d = e.diagnostics()
    _assert(d["status"] == "operational", "pennylane_diagnostics")

def test_pennylane_allocate_device():
    from system.omni_pennylane_qml_engine import OmniPennyLaneQMLEngine
    e = OmniPennyLaneQMLEngine()
    r = e.allocate_device(name="default.qubit", wires=4)
    _assert(r["status"] == "success", "pennylane_allocate_device")
    _assert(r["device"]["wires"] == 4, "pennylane_wires_4")

def test_pennylane_allocate_invalid():
    from system.omni_pennylane_qml_engine import OmniPennyLaneQMLEngine
    e = OmniPennyLaneQMLEngine()
    r = e.allocate_device(name="quantum.supremacy", wires=4)
    _assert(r["status"] == "error", "pennylane_allocate_invalid")

def test_pennylane_define_circuit():
    from system.omni_pennylane_qml_engine import OmniPennyLaneQMLEngine
    e = OmniPennyLaneQMLEngine()
    ops = [
        {"gate": "Hadamard", "wires": [0]},
        {"gate": "RX", "wires": [0], "param_idx": 0},
        {"gate": "CNOT", "wires": [0, 1]}
    ]
    r = e.define_circuit(circuit_id="circ1", operations=ops)
    _assert(r["status"] == "success", "pennylane_define_circuit")
    _assert(r["circuit"]["required_params"] == 1, "pennylane_params_1")

def test_pennylane_circuit_invalid_gate():
    from system.omni_pennylane_qml_engine import OmniPennyLaneQMLEngine
    e = OmniPennyLaneQMLEngine()
    ops = [{"gate": "TesseractGate", "wires": [0]}]
    r = e.define_circuit(circuit_id="circ2", operations=ops)
    _assert(r["status"] == "error", "pennylane_invalid_gate")

def test_pennylane_compile_qnode():
    from system.omni_pennylane_qml_engine import OmniPennyLaneQMLEngine
    e = OmniPennyLaneQMLEngine()
    dev = e.allocate_device("default.qubit", 2)["device"]
    circ = e.define_circuit("c1", [{"gate": "RX", "wires": [0], "param_idx": 0}])["circuit"]
    r = e.compile_qnode(qnode_id="q1", circuit_id=circ["id"], device_id=dev["id"])
    _assert(r["status"] == "success", "pennylane_compile_qnode")

def test_pennylane_compile_invalid():
    from system.omni_pennylane_qml_engine import OmniPennyLaneQMLEngine
    e = OmniPennyLaneQMLEngine()
    r = e.compile_qnode("q1", "nonexistent_circ", "nonexistent_dev")
    _assert(r["status"] == "error", "pennylane_compile_invalid")

def test_pennylane_execute_qnode():
    from system.omni_pennylane_qml_engine import OmniPennyLaneQMLEngine
    e = OmniPennyLaneQMLEngine()
    dev = e.allocate_device("default.qubit", 2)["device"]
    circ = e.define_circuit("c1", [{"gate": "RX", "wires": [0], "param_idx": 0}])["circuit"]
    e.compile_qnode("q1", circ["id"], dev["id"])
    r = e.execute_qnode("q1", params=[1.57])
    _assert(r["status"] == "success", "pennylane_execute")

def test_pennylane_execute_param_mismatch():
    from system.omni_pennylane_qml_engine import OmniPennyLaneQMLEngine
    e = OmniPennyLaneQMLEngine()
    dev = e.allocate_device("default.qubit", 2)["device"]
    circ = e.define_circuit("c1", [{"gate": "RX", "wires": [0], "param_idx": 0}])["circuit"]
    e.compile_qnode("q1", circ["id"], dev["id"])
    r = e.execute_qnode("q1", params=[1.57, 2.0]) # 2 params provided, 1 expected
    _assert(r["status"] == "error", "pennylane_param_mismatch")

def test_pennylane_gradient():
    from system.omni_pennylane_qml_engine import OmniPennyLaneQMLEngine
    e = OmniPennyLaneQMLEngine()
    dev = e.allocate_device("default.qubit", 2)["device"]
    circ = e.define_circuit("c1", [{"gate": "RX", "wires": [0], "param_idx": 0}])["circuit"]
    e.compile_qnode("q1", circ["id"], dev["id"])
    r = e.param_shift_gradient("q1", params=[1.0])
    _assert(r["status"] == "success", "pennylane_gradient")
    _assert(len(r["gradients"]) == 1, "pennylane_grad_length")


# ======================================================================
# ENGINE 2: OmniDamoYoloEngine (10 tests)
# ======================================================================

def test_damo_diagnostics():
    from system.omni_damo_yolo_engine import OmniDamoYoloEngine
    e = OmniDamoYoloEngine()
    d = e.diagnostics()
    _assert(d["status"] == "operational", "damo_diagnostics")

def test_damo_dataset_config():
    from system.omni_damo_yolo_engine import OmniDamoYoloEngine
    e = OmniDamoYoloEngine()
    r = e.configure_dataset("coco", num_classes=80, resolution=640)
    _assert(r["status"] == "success", "damo_dataset")
    _assert(r["dataset"]["num_classes"] == 80, "damo_dataset_classes")

def test_damo_dataset_invalid_res():
    from system.omni_damo_yolo_engine import OmniDamoYoloEngine
    e = OmniDamoYoloEngine()
    r = e.configure_dataset("coco", num_classes=80, resolution=600) # not % 32
    _assert(r["status"] == "error", "damo_dataset_invalid_res")

def test_damo_tinynas_config():
    from system.omni_damo_yolo_engine import OmniDamoYoloEngine
    e = OmniDamoYoloEngine()
    e.configure_dataset("coco", 80)
    r = e.configure_tinynas("yolo_s", "Small", "coco")
    _assert(r["status"] == "success", "damo_tinynas")
    _assert(r["model_config"]["scale"] == "Small", "damo_scale_small")

def test_damo_tinynas_invalid_scale():
    from system.omni_damo_yolo_engine import OmniDamoYoloEngine
    e = OmniDamoYoloEngine()
    e.configure_dataset("coco", 80)
    r = e.configure_tinynas("yolo_s", "Gigantic", "coco")
    _assert(r["status"] == "error", "damo_tinynas_invalid_scale")

def test_damo_distillation():
    from system.omni_damo_yolo_engine import OmniDamoYoloEngine
    e = OmniDamoYoloEngine()
    e.configure_dataset("coco", 80)
    e.configure_tinynas("model_1", "Tiny", "coco")
    r = e.setup_distillation("model_1", "teacher.pth", "Zero-Label")
    _assert(r["status"] == "success", "damo_distillation")

def test_damo_distillation_invalid_model():
    from system.omni_damo_yolo_engine import OmniDamoYoloEngine
    e = OmniDamoYoloEngine()
    r = e.setup_distillation("ghost_model", "teacher.pth")
    _assert(r["status"] == "error", "damo_distillation_invalid_model")

def test_damo_train():
    from system.omni_damo_yolo_engine import OmniDamoYoloEngine
    e = OmniDamoYoloEngine()
    e.configure_dataset("coco", 80)
    e.configure_tinynas("model_1", "Medium", "coco")
    r = e.train_model("model_1", epochs=10, batch_size=32)
    _assert(r["status"] == "success", "damo_train")
    _assert(r["training_result"]["final_mAP"] > 0, "damo_map_computed")

def test_damo_train_invalid():
    from system.omni_damo_yolo_engine import OmniDamoYoloEngine
    e = OmniDamoYoloEngine()
    r = e.train_model("model_2", 10, 32)
    _assert(r["status"] == "error", "damo_train_invalid")

def test_damo_trt_export():
    from system.omni_damo_yolo_engine import OmniDamoYoloEngine
    e = OmniDamoYoloEngine()
    e.configure_dataset("coco", 80)
    e.configure_tinynas("model_1", "Small", "coco", use_repconv=True)
    r = e.export_trt("model_1", "fp16")
    _assert(r["status"] == "success", "damo_trt")
    _assert(r["export"]["reparameterized_layers"] > 0, "damo_repconv")


# ======================================================================
# ENGINE 3: OmniFastNLPEngine (10 tests)
# ======================================================================

def test_fastnlp_diagnostics():
    from system.omni_fastnlp_engine import OmniFastNLPEngine
    e = OmniFastNLPEngine()
    d = e.diagnostics()
    _assert(d["status"] == "operational", "fastnlp_diagnostics")

def test_fastnlp_load_dataset():
    from system.omni_fastnlp_engine import OmniFastNLPEngine
    e = OmniFastNLPEngine()
    data = [{"text": "hello world", "label": "0"}, {"text": "fastnlp is cool", "label": "1"}]
    r = e.load_dataset("ds1", data)
    _assert(r["status"] == "success", "fastnlp_load")
    _assert(r["dataset_info"]["size"] == 2, "fastnlp_size_2")

def test_fastnlp_load_empty():
    from system.omni_fastnlp_engine import OmniFastNLPEngine
    e = OmniFastNLPEngine()
    r = e.load_dataset("ds1", [])
    _assert(r["status"] == "error", "fastnlp_load_empty")

def test_fastnlp_build_vocab():
    from system.omni_fastnlp_engine import OmniFastNLPEngine
    e = OmniFastNLPEngine()
    data = [{"text": "hello world the world", "label": "0"}]
    e.load_dataset("ds1", data)
    r = e.build_vocabulary("v1", "ds1", "text", min_freq=1)
    _assert(r["status"] == "success", "fastnlp_vocab")
    _assert(r["vocabulary"]["total_tokens"] >= 4, "fastnlp_vocab_size") # pad, unk, hello, world, the

def test_fastnlp_vocab_invalid_ds():
    from system.omni_fastnlp_engine import OmniFastNLPEngine
    e = OmniFastNLPEngine()
    r = e.build_vocabulary("v1", "ghost_ds", "text")
    _assert(r["status"] == "error", "fastnlp_vocab_invalid_ds")

def test_fastnlp_configure_pipeline():
    from system.omni_fastnlp_engine import OmniFastNLPEngine
    e = OmniFastNLPEngine()
    r = e.configure_pipeline("p1", ["tokenize", "lower", "index"])
    _assert(r["status"] == "success", "fastnlp_pipeline")

def test_fastnlp_pipeline_invalid():
    from system.omni_fastnlp_engine import OmniFastNLPEngine
    e = OmniFastNLPEngine()
    r = e.configure_pipeline("p1", ["tokenize", "summon_demon"])
    _assert(r["status"] == "error", "fastnlp_pipeline_invalid")

def test_fastnlp_trainer():
    from system.omni_fastnlp_engine import OmniFastNLPEngine
    e = OmniFastNLPEngine()
    data = [{"text": "hi", "label": "1"}] * 10
    e.load_dataset("ds1", data)
    e.configure_pipeline("p1", ["tokenize"])
    r = e.execute_trainer("ds1", "p1", epochs=5, metric="Accuracy")
    _assert(r["status"] == "success", "fastnlp_trainer")
    _assert(len(r["training_report"]["history"]) == 5, "fastnlp_epochs")

def test_fastnlp_trainer_invalid_metric():
    from system.omni_fastnlp_engine import OmniFastNLPEngine
    e = OmniFastNLPEngine()
    data = [{"text": "hi", "label": "1"}]
    e.load_dataset("ds1", data)
    e.configure_pipeline("p1", ["tokenize"])
    r = e.execute_trainer("ds1", "p1", epochs=5, metric="InvalidMetric")
    _assert(r["status"] == "error", "fastnlp_trainer_invalid_metric")

def test_fastnlp_trainer_no_ds():
    from system.omni_fastnlp_engine import OmniFastNLPEngine
    e = OmniFastNLPEngine()
    e.configure_pipeline("p1", ["tokenize"])
    r = e.execute_trainer("ghost_ds", "p1", epochs=5, metric="Accuracy")
    _assert(r["status"] == "error", "fastnlp_trainer_no_ds")


# ======================================================================
# ENGINE 4: OmniTSFForecastingEngine (10 tests)
# ======================================================================

def test_tsf_diagnostics():
    from system.omni_tsf_forecasting_engine import OmniTSFForecastingEngine
    e = OmniTSFForecastingEngine()
    d = e.diagnostics()
    _assert(d["status"] == "operational", "tsf_diagnostics")

def test_tsf_register_series():
    from system.omni_tsf_forecasting_engine import OmniTSFForecastingEngine
    e = OmniTSFForecastingEngine()
    r = e.register_series("ettm1", total_length=1000, num_features=7, freq="h")
    _assert(r["status"] == "success", "tsf_register")

def test_tsf_register_invalid_len():
    from system.omni_tsf_forecasting_engine import OmniTSFForecastingEngine
    e = OmniTSFForecastingEngine()
    r = e.register_series("ettm1", total_length=50, num_features=7, freq="h")
    _assert(r["status"] == "error", "tsf_register_invalid_len")

def test_tsf_configure_model():
    from system.omni_tsf_forecasting_engine import OmniTSFForecastingEngine
    e = OmniTSFForecastingEngine()
    r = e.configure_model("m1", "Autoformer", seq_len=96, label_len=48, pred_len=24)
    _assert(r["status"] == "success", "tsf_model")
    _assert(r["model"]["decomposition"] is True, "tsf_decomposition_enabled")

def test_tsf_configure_invalid_len():
    from system.omni_tsf_forecasting_engine import OmniTSFForecastingEngine
    e = OmniTSFForecastingEngine()
    r = e.configure_model("m1", "Informer", seq_len=48, label_len=96, pred_len=24)
    _assert(r["status"] == "error", "tsf_model_invalid_len")

def test_tsf_generate_windows():
    from system.omni_tsf_forecasting_engine import OmniTSFForecastingEngine
    e = OmniTSFForecastingEngine()
    e.register_series("s1", 1000, 7, "h")
    r = e.generate_windows("s1", 96, 24)
    _assert(r["status"] == "success", "tsf_windows")
    _assert(r["windows"]["total_extracted"] == (1000 - 120 + 1), "tsf_window_count")

def test_tsf_generate_windows_toolong():
    from system.omni_tsf_forecasting_engine import OmniTSFForecastingEngine
    e = OmniTSFForecastingEngine()
    e.register_series("s1", 500, 7, "h")
    r = e.generate_windows("s1", 900, 24)
    _assert(r["status"] == "error", "tsf_windows_too_long")

def test_tsf_simulate_forecast():
    from system.omni_tsf_forecasting_engine import OmniTSFForecastingEngine
    e = OmniTSFForecastingEngine()
    e.register_series("s1", 1000, 7, "h")
    e.configure_model("m1", "Autoformer", 96, 48, 24)
    r = e.execute_forecast("m1", "s1")
    _assert(r["status"] == "success", "tsf_forecast")
    _assert("MSE" in r["forecast_results"]["metrics"], "tsf_mse")
    _assert(r["forecast_results"]["metrics"]["MSE"] > 0, "tsf_mse_positive")

def test_tsf_forecast_invalid_model():
    from system.omni_tsf_forecasting_engine import OmniTSFForecastingEngine
    e = OmniTSFForecastingEngine()
    e.register_series("s1", 1000, 7, "h")
    r = e.execute_forecast("ghost_model", "s1")
    _assert(r["status"] == "error", "tsf_forecast_no_model")

def test_tsf_forecast_invalid_ds():
    from system.omni_tsf_forecasting_engine import OmniTSFForecastingEngine
    e = OmniTSFForecastingEngine()
    e.configure_model("m1", "Autoformer", 96, 48, 24)
    r = e.execute_forecast("m1", "ghost_s1")
    _assert(r["status"] == "error", "tsf_forecast_no_ds")


# ======================================================================
# ENGINE 5: OmniUVADeepLearningEngine (10 tests)
# ======================================================================

def test_uva_diagnostics():
    from system.omni_uva_dl_course_engine import OmniUVADeepLearningEngine
    e = OmniUVADeepLearningEngine()
    d = e.diagnostics()
    _assert(d["status"] == "operational", "uva_diagnostics")

def test_uva_register_learner():
    from system.omni_uva_dl_course_engine import OmniUVADeepLearningEngine
    e = OmniUVADeepLearningEngine()
    r = e.register_learner("student_1", "JAX")
    _assert(r["status"] == "success", "uva_register")
    _assert(r["profile"]["framework"] == "JAX", "uva_framework")

def test_uva_register_invalid_fw():
    from system.omni_uva_dl_course_engine import OmniUVADeepLearningEngine
    e = OmniUVADeepLearningEngine()
    r = e.register_learner("student_1", "TensorFlow")
    _assert(r["status"] == "error", "uva_register_invalid")

def test_uva_get_curriculum():
    from system.omni_uva_dl_course_engine import OmniUVADeepLearningEngine
    e = OmniUVADeepLearningEngine()
    r = e.get_curriculum()
    _assert(r["status"] == "success", "uva_curriculum")
    _assert("module_3" in r["curriculum"], "uva_module_3")

def test_uva_execute_module():
    from system.omni_uva_dl_course_engine import OmniUVADeepLearningEngine
    e = OmniUVADeepLearningEngine()
    e.register_learner("stu1", "PyTorch")
    r = e.execute_module("stu1", "module_1", {"learning_rate": 0.001, "epochs": 20})
    _assert(r["status"] == "success", "uva_execute")
    _assert(r["execution"]["passed"] is True, "uva_passed")

def test_uva_execute_fail():
    from system.omni_uva_dl_course_engine import OmniUVADeepLearningEngine
    e = OmniUVADeepLearningEngine()
    e.register_learner("stu1", "PyTorch")
    # Terrible LR should cause failure or low score
    r = e.execute_module("stu1", "module_5", {"learning_rate": 10.0, "epochs": 1})
    _assert(r["status"] == "success", "uva_execute_fail_score")
    _assert(r["execution"]["passed"] is False, "uva_failed")

def test_uva_execute_invalid_learner():
    from system.omni_uva_dl_course_engine import OmniUVADeepLearningEngine
    e = OmniUVADeepLearningEngine()
    r = e.execute_module("ghost", "module_1", {})
    _assert(r["status"] == "error", "uva_execute_no_learner")

def test_uva_execute_invalid_module():
    from system.omni_uva_dl_course_engine import OmniUVADeepLearningEngine
    e = OmniUVADeepLearningEngine()
    e.register_learner("stu1", "PyTorch")
    r = e.execute_module("stu1", "module_99", {"epochs": 10})
    _assert(r["status"] == "error", "uva_execute_no_module")

def test_uva_validate_flow():
    from system.omni_uva_dl_course_engine import OmniUVADeepLearningEngine
    e = OmniUVADeepLearningEngine()
    r = e.validate_flow_concept("forward", jacobian_det=1.5)
    _assert(r["status"] == "success", "uva_flow_valid")
    _assert(r["concept_check"]["valid"] is True, "uva_jacobian_valid")

def test_uva_validate_flow_invalid():
    from system.omni_uva_dl_course_engine import OmniUVADeepLearningEngine
    e = OmniUVADeepLearningEngine()
    r = e.validate_flow_concept("inverse", jacobian_det=-0.5)
    _assert(r["status"] == "success", "uva_flow_invalid")
    _assert(r["concept_check"]["valid"] is False, "uva_jacobian_invalid")


# ======================================================================
# RUNNER
# ======================================================================

def main():
    all_tests = [
        # PennyLane
        test_pennylane_diagnostics, test_pennylane_allocate_device, test_pennylane_allocate_invalid,
        test_pennylane_define_circuit, test_pennylane_circuit_invalid_gate, test_pennylane_compile_qnode,
        test_pennylane_compile_invalid, test_pennylane_execute_qnode, test_pennylane_execute_param_mismatch,
        test_pennylane_gradient,
        # DAMO-YOLO
        test_damo_diagnostics, test_damo_dataset_config, test_damo_dataset_invalid_res,
        test_damo_tinynas_config, test_damo_tinynas_invalid_scale, test_damo_distillation,
        test_damo_distillation_invalid_model, test_damo_train, test_damo_train_invalid,
        test_damo_trt_export,
        # FastNLP
        test_fastnlp_diagnostics, test_fastnlp_load_dataset, test_fastnlp_load_empty,
        test_fastnlp_build_vocab, test_fastnlp_vocab_invalid_ds, test_fastnlp_configure_pipeline,
        test_fastnlp_pipeline_invalid, test_fastnlp_trainer, test_fastnlp_trainer_invalid_metric,
        test_fastnlp_trainer_no_ds,
        # TSF Forecasting
        test_tsf_diagnostics, test_tsf_register_series, test_tsf_register_invalid_len,
        test_tsf_configure_model, test_tsf_configure_invalid_len, test_tsf_generate_windows,
        test_tsf_generate_windows_toolong, test_tsf_simulate_forecast, test_tsf_forecast_invalid_model,
        test_tsf_forecast_invalid_ds,
        # UvA Deep Learning
        test_uva_diagnostics, test_uva_register_learner, test_uva_register_invalid_fw,
        test_uva_get_curriculum, test_uva_execute_module, test_uva_execute_fail,
        test_uva_execute_invalid_learner, test_uva_execute_invalid_module,
        test_uva_validate_flow, test_uva_validate_flow_invalid
    ]

    print(f"\n{'='*60}")
    print(f"  OMNI BATCH 5 (Semester 7) — Integration Test Suite")
    print(f"  Total Tests: {len(all_tests)}")
    print(f"{'='*60}\n")

    for test_fn in all_tests:
        _run(test_fn, test_fn.__name__)

    print(f"\n{'='*60}")
    print(f"  Results: {_PASS} PASSED | {_FAIL} FAILED | {_PASS + _FAIL} TOTAL")
    print(f"{'='*60}")

    if _ERRORS:
        print("\nFailures/Errors:")
        for err in _ERRORS:
            print(f"  [ERROR] {err}")

    return _FAIL == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
