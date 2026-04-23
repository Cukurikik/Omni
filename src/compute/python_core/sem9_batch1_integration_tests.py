"""
OMNI Semester 9 - Batch 1 Integration Tests
=============================================
Comprehensive integration and unit testing suite for Semester 9 Batch 1.
Validates:
1. OmniApkidEngine
2. OmniKomputeEngine
3. OmniHamiltonEngine
4. OmniEvaluateEngine
5. OmniAlanSdkWebEngine

Ensures absolute compliance with CODE RULE 003.
"""

import unittest
import numpy as np

# Suppress debug logs during testing
import logging
logging.getLogger("OmniAIAudioDatasetsEngine").setLevel(logging.ERROR)

from omni_apkid_engine import OmniApkidEngine, Ok as ApkidOk, Err as ApkidErr, YaraRuleProd
from omni_kompute_engine import OmniKomputeEngine, Ok as K_Ok, Err as K_Err
from omni_hamilton_engine import OmniHamiltonEngine, Ok as H_Ok, Err as H_Err
from omni_evaluate_engine import OmniEvaluateEngine, Ok as E_Ok, Err as E_Err
from omni_alan_sdk_web_engine import OmniAlanSdkWebEngine, Ok as A_Ok, Err as A_Err, ConnectionState

class TestOmniSemester9Batch1(unittest.TestCase):

    # ---------------------------------------------------------
    # 1. OmniApkidEngine Tests
    # ---------------------------------------------------------
    def test_apkid_engine_initialization(self):
        engine = OmniApkidEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")
        self.assertGreater(diag["rules_loaded"], 0)

    def test_apkid_scan_buffer_match(self):
        engine = OmniApkidEngine()
        # Proding an APK payload containing a known rule defined in engine (proguard_map)
        payload = b"HEADER\x00\x01\x02proguard_map\x00FOOTER"
        res = engine.analyze_payload(payload)
        
        self.assertIsInstance(res, ApkidOk)
        matches = res.value
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0]["rule"], "obfuscator_proguard")

    def test_apkid_scan_buffer_no_match(self):
        engine = OmniApkidEngine()
        payload = b"CLEAN_PAYLOAD_NO_SIGNATURES"
        res = engine.analyze_payload(payload)
        
        self.assertIsInstance(res, ApkidOk)
        matches = res.value
        self.assertEqual(len(matches), 0)

    # ---------------------------------------------------------
    # 2. OmniKomputeEngine Tests
    # ---------------------------------------------------------
    def test_kompute_engine_diagnostics(self):
        engine = OmniKomputeEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_kompute_add_shader_simulation(self):
        engine = OmniKomputeEngine()
        arr1 = [1.5, 2.5, 3.5]
        arr2 = [0.5, 1.5, 0.5]
        res = engine.execute_add_shader(arr1, arr2)
        
        self.assertIsInstance(res, K_Ok)
        out = res.value
        self.assertAlmostEqual(out[0], 2.0)
        self.assertAlmostEqual(out[1], 4.0)
        self.assertAlmostEqual(out[2], 4.0)

    def test_kompute_mismatched_arrays(self):
        engine = OmniKomputeEngine()
        res = engine.execute_add_shader([1.0], [1.0, 2.0])
        self.assertIsInstance(res, K_Err)

    # ---------------------------------------------------------
    # 3. OmniHamiltonEngine Tests
    # ---------------------------------------------------------
    def test_hamilton_engine_diagnostics(self):
        engine = OmniHamiltonEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_hamilton_dag_execution(self):
        # algebraic_bound module consisting of top-level functional bindings
        def get_a(a_input: int) -> int: return a_input * 2
        def get_b(a_input: int) -> int: return a_input + 5
        def compute_c(get_a: int, get_b: int) -> int: return get_a + get_b

        module = {
            "get_a": get_a,
            "get_b": get_b,
            "compute_c": compute_c
        }

        engine = OmniHamiltonEngine()
        res_build = engine.build_graph(module)
        self.assertIsInstance(res_build, H_Ok)

        # Execute
        res_exec = engine.execute_flow(["compute_c"], {"a_input": 10})
        self.assertIsInstance(res_exec, H_Ok)
        
        # a_input=10 -> get_a=20, get_b=15 -> compute_c = 35
        out = res_exec.value
        self.assertEqual(out["compute_c"], 35)

    def test_hamilton_missing_dependency(self):
        def compute_c(missing_dep: int) -> int: return missing_dep
        engine = OmniHamiltonEngine()
        engine.build_graph({"compute_c": compute_c})
        
        res = engine.execute_flow(["compute_c"], {}) # missing input
        self.assertIsInstance(res, H_Err)

    # ---------------------------------------------------------
    # 4. OmniEvaluateEngine Tests
    # ---------------------------------------------------------
    def test_evaluate_engine_diagnostics(self):
        engine = OmniEvaluateEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_evaluate_accuracy_metric(self):
        engine = OmniEvaluateEngine()
        preds = [1, 0, 1, 1]
        refs =  [1, 0, 0, 1]
        
        res = engine.compute_metric("accuracy", preds, refs)
        self.assertIsInstance(res, E_Ok)
        self.assertAlmostEqual(res.value["accuracy"], 0.75)

    def test_evaluate_f1_metric(self):
        engine = OmniEvaluateEngine()
        preds = [1, 1, 0, 0]
        refs =  [1, 0, 1, 0]
        
        # TP=1, FP=1, FN=1 -> Prec = 0.5, Rec = 0.5 -> F1 = 0.5
        res = engine.compute_metric("f1", preds, refs)
        self.assertIsInstance(res, E_Ok)
        self.assertAlmostEqual(res.value["f1"], 0.5)

    def test_evaluate_invalid_metric(self):
        engine = OmniEvaluateEngine()
        res = engine.compute_metric("unknown_metric", [1], [1])
        self.assertIsInstance(res, E_Err)

    # ---------------------------------------------------------
    # 5. OmniAlanSdkWebEngine Tests
    # ---------------------------------------------------------
    def test_alan_sdk_engine_diagnostics(self):
        engine = OmniAlanSdkWebEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_alan_lifecycle_simulation(self):
        engine = OmniAlanSdkWebEngine()
        key = "project_secret_xyz"
        
        # Create
        res_create = engine.create_instance(key)
        self.assertIsInstance(res_create, A_Ok)
        
        # Handshake
        res_handshake = engine.execute_handshake(key)
        self.assertIsInstance(res_handshake, A_Ok)
        
        protocol = res_create.value
        self.assertEqual(protocol.conn_state, ConnectionState.AUTHORIZED)

        # Synchronize Context
        res_sync = protocol.set_visual_state({"screen": "dashboard"})
        self.assertIsInstance(res_sync, A_Ok)
        
        # Voice routing
        res_voice = protocol.emit_voice_command("refresh data")
        self.assertIsInstance(res_voice, A_Ok)
        
        # TTS Dispatch
        res_tts = protocol.play_tts("Data sequence refreshed.")
        self.assertIsInstance(res_tts, A_Ok)

        # Log Check
        expected_logs = [
            "connection_established",
            "authorized",
            "visual_state_sync: ['screen']",
            "state_listen",
            "cmd_ingest: refresh data",
            "state_idle",
            "tts_play: Data sequence refreshed."
        ]
        self.assertEqual(len(protocol.event_log), 7)
        self.assertEqual(protocol.event_log, expected_logs)

    def test_alan_unauthorized_action(self):
        engine = OmniAlanSdkWebEngine()
        key = "project_secret_xyz"
        res_create = engine.create_instance(key)
        protocol = res_create.value
        
        # Attempt operation without proper handshake
        res_voice = protocol.emit_voice_command("hello")
        self.assertIsInstance(res_voice, A_Err)


if __name__ == "__main__":
    unittest.main()
