# -*- coding: utf-8 -*-
"""
OMNI SEMESTER 7 — BATCH 8 INTEGRATION TESTS
Validating 5 New Omni Engines against Zero-algebraic_bound Monadic constraints.
Contains 50 comprehensive unit tests (10 per engine).
"""

import unittest
from src.compute.python_core.system.omni_prompttools_engine import OmniPrompttoolsEngine
from src.compute.python_core.system.omni_imgclsmob_engine import OmniImgclsmobEngine
from src.compute.python_core.system.omni_quality_scaler_engine import OmniQualityScalerEngine
from src.compute.python_core.system.omni_super_slomo_engine import OmniSuperSloMoEngine
from src.compute.python_core.system.omni_pytorch_geometric_temporal_engine import OmniPyTorchGeometricTemporalEngine

class TestBatch8Semester7(unittest.TestCase):
    
    # ==========================
    # 1. OmniPrompttoolsEngine (10 tests)
    # ==========================
    def setUp_prompt(self):
        return OmniPrompttoolsEngine()

    def test_prompt_diagnostics(self):
        eng = self.setUp_prompt()
        self.assertEqual(eng.diagnostics()["status"], "operational")

    def test_prompt_init_success(self):
        eng = self.setUp_prompt()
        res = eng.initialize_prompt_experiment("exp_1", "You are an AI.", [{"temp": 0.5}, {"temp": 0.9}])
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["experiment"]["variants"]), 2)

    def test_prompt_init_duplicate(self):
        eng = self.setUp_prompt()
        eng.initialize_prompt_experiment("exp_1", "sys", [{"t": 1}])
        res = eng.initialize_prompt_experiment("exp_1", "sys2", [{"t": 2}])
        self.assertEqual(res["status"], "error")

    def test_prompt_init_empty_prompt(self):
        eng = self.setUp_prompt()
        res = eng.initialize_prompt_experiment("exp_1", "", [{"t": 1}])
        self.assertEqual(res["status"], "error")

    def test_prompt_init_empty_variants(self):
        eng = self.setUp_prompt()
        res = eng.initialize_prompt_experiment("exp_1", "sys", [])
        self.assertEqual(res["status"], "error")

    def test_prompt_execute_success(self):
        eng = self.setUp_prompt()
        eng.initialize_prompt_experiment("exp_1", "sys", [{"temperature": 0.2}, {"temperature": 0.8}])
        res = eng.execute_llm_call("exp_1", 1)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["execution_result"]["variant_index"], 1)

    def test_prompt_execute_invalid_variant(self):
        eng = self.setUp_prompt()
        eng.initialize_prompt_experiment("exp_1", "sys", [{"temperature": 0.2}])
        res = eng.execute_llm_call("exp_1", 5)
        self.assertEqual(res["status"], "error")

    def test_prompt_execute_missing_experiment(self):
        eng = self.setUp_prompt()
        res = eng.execute_llm_call("missing", 0)
        self.assertEqual(res["status"], "error")

    def test_prompt_eval_success(self):
        eng = self.setUp_prompt()
        eng.initialize_prompt_experiment("exp_1", "sys", [{"temperature": 0.5}])
        eng.execute_llm_call("exp_1", 0)
        res = eng.evaluate_semantic_similarity("exp_1", "Expected ground truth here")
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["evaluations"]), 1)

    def test_prompt_eval_incomplete(self):
        eng = self.setUp_prompt()
        eng.initialize_prompt_experiment("exp_1", "sys", [{"temperature": 0.5}, {"temperature": 0.8}])
        eng.execute_llm_call("exp_1", 0) # Missed variant 1
        res = eng.evaluate_semantic_similarity("exp_1", "Truth")
        self.assertEqual(res["status"], "error")


    # ==========================
    # 2. OmniImgclsmobEngine (10 tests)
    # ==========================
    def setUp_imgcls(self):
        return OmniImgclsmobEngine()

    def test_imgcls_diagnostics(self):
        eng = self.setUp_imgcls()
        self.assertEqual(eng.diagnostics()["status"], "operational")

    def test_imgcls_load_success(self):
        eng = self.setUp_imgcls()
        res = eng.load_mobile_classification_graph("mobilenet", 224)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["graph_properties"]["resolution"], 224)

    def test_imgcls_load_unsupported(self):
        eng = self.setUp_imgcls()
        res = eng.load_mobile_classification_graph("resnet152", 224)
        self.assertEqual(res["status"], "error")

    def test_imgcls_load_invalid_res(self):
        eng = self.setUp_imgcls()
        res = eng.load_mobile_classification_graph("mobilenet", -1)
        self.assertEqual(res["status"], "error")

    def test_imgcls_quantize_success(self):
        eng = self.setUp_imgcls()
        gid = eng.load_mobile_classification_graph("mobilenet")["graph_id"]
        res = eng.quantize_weights_int8(gid)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["quantization"], "INT8")

    def test_imgcls_quantize_missing_graph(self):
        eng = self.setUp_imgcls()
        res = eng.quantize_weights_int8("missing")
        self.assertEqual(res["status"], "error")

    def test_imgcls_quantize_already_quantized(self):
        eng = self.setUp_imgcls()
        gid = eng.load_mobile_classification_graph("mobilenet")["graph_id"]
        eng.quantize_weights_int8(gid)
        res = eng.quantize_weights_int8(gid)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["message"], "Graph already quantized.")

    def test_imgcls_inference_success(self):
        eng = self.setUp_imgcls()
        gid = eng.load_mobile_classification_graph("mobilenet")["graph_id"]
        res = eng.execute_edge_inference(gid, [0.5, 0.1, 0.9])
        self.assertEqual(res["status"], "success")
        self.assertTrue("inference_class" in res)

    def test_imgcls_inference_empty_input(self):
        eng = self.setUp_imgcls()
        gid = eng.load_mobile_classification_graph("mobilenet")["graph_id"]
        res = eng.execute_edge_inference(gid, [])
        self.assertEqual(res["status"], "error")

    def test_imgcls_inference_metrics_quantized_vs_float(self):
        eng = self.setUp_imgcls()
        gid_float = eng.load_mobile_classification_graph("squeezenet")["graph_id"]
        gid_quant = eng.load_mobile_classification_graph("squeezenet")["graph_id"]
        eng.quantize_weights_int8(gid_quant)
        
        res_float = eng.execute_edge_inference(gid_float, [1.0])
        res_quant = eng.execute_edge_inference(gid_quant, [1.0])
        
        self.assertTrue(res_quant["metrics"]["latency_ms"] < res_float["metrics"]["latency_ms"])


    # ==========================
    # 3. OmniQualityScalerEngine (10 tests)
    # ==========================
    def setUp_scaler(self):
        return OmniQualityScalerEngine()

    def test_scaler_diagnostics(self):
        eng = self.setUp_scaler()
        self.assertEqual(eng.diagnostics()["status"], "operational")

    def test_scaler_init_success(self):
        eng = self.setUp_scaler()
        res = eng.initialize_upscaler_model("Real-ESRGAN", 4)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["config"]["scale"], 4)

    def test_scaler_init_unsupported(self):
        eng = self.setUp_scaler()
        res = eng.initialize_upscaler_model("FakeGAN", 4)
        self.assertEqual(res["status"], "error")

    def test_scaler_init_invalid_scale(self):
        eng = self.setUp_scaler()
        res = eng.initialize_upscaler_model("BSRGAN", 5)
        self.assertEqual(res["status"], "error")

    def test_scaler_apply_success(self):
        eng = self.setUp_scaler()
        sid = eng.initialize_upscaler_model("BSRGAN", 2)["session_id"]
        res = eng.apply_super_resolution_frame(sid, 1920, 1080)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["upscaled_dim"], "3840x2160")

    def test_scaler_apply_invalid_dim(self):
        eng = self.setUp_scaler()
        sid = eng.initialize_upscaler_model("BSRGAN", 2)["session_id"]
        res = eng.apply_super_resolution_frame(sid, 0, 1080)
        self.assertEqual(res["status"], "error")

    def test_scaler_apply_missing_session(self):
        eng = self.setUp_scaler()
        res = eng.apply_super_resolution_frame("missing", 500, 500)
        self.assertEqual(res["status"], "error")

    def test_scaler_apply_oom_protection(self):
        eng = self.setUp_scaler()
        sid = eng.initialize_upscaler_model("BSRGAN", 8)["session_id"]
        res = eng.apply_super_resolution_frame(sid, 8000, 8000) # Gigantic image
        self.assertEqual(res["status"], "error")
        self.assertTrue("OOM Protection" in res["message"])

    def test_scaler_export_success(self):
        eng = self.setUp_scaler()
        sid = eng.initialize_upscaler_model("BSRGAN", 2)["session_id"]
        eng.apply_super_resolution_frame(sid, 1280, 720)
        res = eng.export_scaled_media(sid, "png")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["frames_exported"], 1)

    def test_scaler_export_no_frames(self):
        eng = self.setUp_scaler()
        sid = eng.initialize_upscaler_model("BSRGAN", 2)["session_id"]
        res = eng.export_scaled_media(sid, "jpg")
        self.assertEqual(res["status"], "error")


    # ==========================
    # 4. OmniSuperSloMoEngine (10 tests)
    # ==========================
    def setUp_slomo(self):
        return OmniSuperSloMoEngine()

    def test_slomo_diagnostics(self):
        eng = self.setUp_slomo()
        self.assertEqual(eng.diagnostics()["status"], "operational")

    def test_slomo_load_success(self):
        eng = self.setUp_slomo()
        res = eng.load_slomo_unet_weights(4)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["config"]["factor"], 4)

    def test_slomo_load_invalid_factor(self):
        eng = self.setUp_slomo()
        res = eng.load_slomo_unet_weights(1)
        self.assertEqual(res["status"], "error")

    def test_slomo_interpolate_success(self):
        eng = self.setUp_slomo()
        pid = eng.load_slomo_unet_weights(4)["pipeline_id"]
        res = eng.interpolate_bidirectional_frames(pid, "frame_0", "frame_1")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["new_frames_generated"], 3)
        self.assertEqual(len(res["sequence"]), 5) # t0 + 3 inter + t1

    def test_slomo_interpolate_missing_pipeline(self):
        eng = self.setUp_slomo()
        res = eng.interpolate_bidirectional_frames("missing", "f0", "f1")
        self.assertEqual(res["status"], "error")

    def test_slomo_interpolate_missing_frames(self):
        eng = self.setUp_slomo()
        pid = eng.load_slomo_unet_weights(4)["pipeline_id"]
        res = eng.interpolate_bidirectional_frames(pid, "", "frame_1")
        self.assertEqual(res["status"], "error")

    def test_slomo_compile_success(self):
        eng = self.setUp_slomo()
        pid = eng.load_slomo_unet_weights(4)["pipeline_id"]
        eng.interpolate_bidirectional_frames(pid, "f0", "f1")
        res = eng.compile_slow_motion_video(pid, 30)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["output_slow_motion_fps"], 30)
        self.assertEqual(res["output_high_framerate_fps"], 120)

    def test_slomo_compile_empty(self):
        eng = self.setUp_slomo()
        pid = eng.load_slomo_unet_weights(4)["pipeline_id"]
        res = eng.compile_slow_motion_video(pid, 30)
        self.assertEqual(res["status"], "error")

    def test_slomo_compile_missing_pipeline(self):
        eng = self.setUp_slomo()
        res = eng.compile_slow_motion_video("missing", 30)
        self.assertEqual(res["status"], "error")

    def test_slomo_compile_invalid_fps(self):
        eng = self.setUp_slomo()
        pid = eng.load_slomo_unet_weights(4)["pipeline_id"]
        eng.interpolate_bidirectional_frames(pid, "f0", "f1")
        res = eng.compile_slow_motion_video(pid, 0)
        self.assertEqual(res["status"], "error")


    # ==========================
    # 5. OmniPyTorchGeometricTemporalEngine (10 tests)
    # ==========================
    def setUp_pyt_geom(self):
        return OmniPyTorchGeometricTemporalEngine()

    def test_pytgeom_diagnostics(self):
        eng = self.setUp_pyt_geom()
        self.assertEqual(eng.diagnostics()["status"], "operational")

    def test_pytgeom_init_success(self):
        eng = self.setUp_pyt_geom()
        res = eng.initialize_dynamic_graph("g1", 16)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["graph_config"]["features"], 16)

    def test_pytgeom_init_duplicate(self):
        eng = self.setUp_pyt_geom()
        eng.initialize_dynamic_graph("g1", 16)
        res = eng.initialize_dynamic_graph("g1", 32)
        self.assertEqual(res["status"], "error")

    def test_pytgeom_init_invalid_features(self):
        eng = self.setUp_pyt_geom()
        res = eng.initialize_dynamic_graph("g1", -5)
        self.assertEqual(res["status"], "error")

    def test_pytgeom_apply_layer_success(self):
        eng = self.setUp_pyt_geom()
        eng.initialize_dynamic_graph("g1", 16)
        res = eng.apply_temporal_gcn("g1", "TGCN", 20)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["fitted_layer"], "TGCN")

    def test_pytgeom_apply_unsupported_layer(self):
        eng = self.setUp_pyt_geom()
        eng.initialize_dynamic_graph("g1", 16)
        res = eng.apply_temporal_gcn("g1", "MAGIC", 20)
        self.assertEqual(res["status"], "error")

    def test_pytgeom_apply_invalid_time(self):
        eng = self.setUp_pyt_geom()
        eng.initialize_dynamic_graph("g1", 16)
        res = eng.apply_temporal_gcn("g1", "TGCN", 0)
        self.assertEqual(res["status"], "error")

    def test_pytgeom_predict_success(self):
        eng = self.setUp_pyt_geom()
        eng.initialize_dynamic_graph("g1", 16)
        eng.apply_temporal_gcn("g1", "DCRNN", 10)
        res = eng.predict_node_evolution("g1", 2)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["horizon"], 2)
        self.assertEqual(len(res["temporal_deltas"]), 2)

    def test_pytgeom_predict_unfitted(self):
        eng = self.setUp_pyt_geom()
        eng.initialize_dynamic_graph("g1", 16)
        res = eng.predict_node_evolution("g1", 2)
        self.assertEqual(res["status"], "error")

    def test_pytgeom_predict_missing_graph(self):
        eng = self.setUp_pyt_geom()
        res = eng.predict_node_evolution("missing", 2)
        self.assertEqual(res["status"], "error")


if __name__ == "__main__":
    unittest.main()
