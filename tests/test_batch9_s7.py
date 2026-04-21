# -*- coding: utf-8 -*-
"""
OMNI SEMESTER 7 — BATCH 9 INTEGRATION TESTS
Validating 5 New Omni Engines against Zero-Mock Monadic constraints.
Contains 50 comprehensive unit tests (10 per engine).
"""

import unittest

# Import the 5 new engines
from src.compute.python_core.system.omni_habitat_lab_engine import OmniHabitatLabEngine
from src.compute.python_core.system.omni_keras_tensorflow_engine import OmniKerasTensorflowEngine
from src.compute.python_core.system.omni_nlp_architect_engine import OmniNlpArchitectEngine
from src.compute.python_core.system.omni_ultralytics_pro_engine import OmniUltralyticsProEngine
from src.compute.python_core.system.omni_awesome_mlss_engine import OmniAwesomeMlssEngine

class TestBatch9Semester7(unittest.TestCase):
    
    # ==========================
    # 1. OmniHabitatLabEngine (10 tests)
    # ==========================
    def setUp_habitat(self):
        return OmniHabitatLabEngine()

    def test_hab_diagnostics(self):
        eng = self.setUp_habitat()
        self.assertEqual(eng.diagnostics()["status"], "operational")

    def test_hab_init_success(self):
        eng = self.setUp_habitat()
        res = eng.initialize_embodied_environment("mp3d", ["RGB", "DEPTH"])
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["config_schema"]["sensors_attached"], 2)

    def test_hab_init_empty_scene(self):
        eng = self.setUp_habitat()
        res = eng.initialize_embodied_environment("", ["RGB"])
        self.assertEqual(res["status"], "error")

    def test_hab_init_empty_sensor(self):
        eng = self.setUp_habitat()
        res = eng.initialize_embodied_environment("mp3d", [])
        self.assertEqual(res["status"], "error")

    def test_hab_execute_success(self):
        eng = self.setUp_habitat()
        eid = eng.initialize_embodied_environment("mp3d", ["RGB"])["environment_id"]
        res = eng.execute_embodied_action(eid, "MOVE_FORWARD")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["action_executed"], "MOVE_FORWARD")

    def test_hab_execute_invalid_action(self):
        eng = self.setUp_habitat()
        eid = eng.initialize_embodied_environment("mp3d", ["RGB"])["environment_id"]
        res = eng.execute_embodied_action(eid, "JUMP")
        self.assertEqual(res["status"], "error")

    def test_hab_execute_invalid_env(self):
        eng = self.setUp_habitat()
        res = eng.execute_embodied_action("missing", "MOVE_FORWARD")
        self.assertEqual(res["status"], "error")

    def test_hab_query_navmesh_success(self):
        eng = self.setUp_habitat()
        eid = eng.initialize_embodied_environment("mp3d", ["RGB"])["environment_id"]
        res = eng.query_navmesh_topology(eid)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["navmesh_metrics"]["connected_components"])

    def test_hab_query_navmesh_missing(self):
        eng = self.setUp_habitat()
        res = eng.query_navmesh_topology("missing")
        self.assertEqual(res["status"], "error")

    def test_hab_step_latency_metric(self):
        eng = self.setUp_habitat()
        eid = eng.initialize_embodied_environment("mp3d", ["RGB"])["environment_id"]
        res = eng.execute_embodied_action(eid, "TURN_LEFT")
        self.assertTrue(res["metrics"]["step_latency_ms"] > 0)


    # ==========================
    # 2. OmniKerasTensorflowEngine (10 tests)
    # ==========================
    def setUp_ktf(self):
        return OmniKerasTensorflowEngine()

    def test_ktf_diagnostics(self):
        eng = self.setUp_ktf()
        self.assertEqual(eng.diagnostics()["status"], "operational")

    def test_ktf_construct_success(self):
        eng = self.setUp_ktf()
        res = eng.construct_sequential_graph("net1", [{"type": "Dense", "units": 10}])
        self.assertEqual(res["status"], "success")

    def test_ktf_construct_empty_name(self):
        eng = self.setUp_ktf()
        res = eng.construct_sequential_graph("", [{"type": "Dense"}])
        self.assertEqual(res["status"], "error")

    def test_ktf_construct_duplicate(self):
        eng = self.setUp_ktf()
        eng.construct_sequential_graph("net1", [{"type": "Dense", "units": 10}])
        res = eng.construct_sequential_graph("net1", [{"type": "Dense", "units": 10}])
        self.assertEqual(res["status"], "error")

    def test_ktf_compile_success(self):
        eng = self.setUp_ktf()
        eng.construct_sequential_graph("net1", [{"type": "Dense", "units": 10}])
        res = eng.compile_distributed_strategy("net1", "adam")
        self.assertEqual(res["status"], "success")

    def test_ktf_compile_invalid_optimizer(self):
        eng = self.setUp_ktf()
        eng.construct_sequential_graph("net1", [{"type": "Dense", "units": 10}])
        res = eng.compile_distributed_strategy("net1", "magic_opt")
        self.assertEqual(res["status"], "error")

    def test_ktf_compile_missing(self):
        eng = self.setUp_ktf()
        res = eng.compile_distributed_strategy("net1")
        self.assertEqual(res["status"], "error")

    def test_ktf_train_success(self):
        eng = self.setUp_ktf()
        eng.construct_sequential_graph("net1", [{"type": "Dense", "units": 10}])
        eng.compile_distributed_strategy("net1")
        res = eng.execute_gradient_epochs("net1", 5, 32)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["training_report"]["epochs_completed"], 5)

    def test_ktf_train_uncompiled(self):
        eng = self.setUp_ktf()
        eng.construct_sequential_graph("net1", [{"type": "Dense", "units": 10}])
        res = eng.execute_gradient_epochs("net1", 5)
        self.assertEqual(res["status"], "error")

    def test_ktf_train_invalid_epochs(self):
        eng = self.setUp_ktf()
        eng.construct_sequential_graph("net1", [{"type": "Dense", "units": 10}])
        eng.compile_distributed_strategy("net1")
        res = eng.execute_gradient_epochs("net1", -1)
        self.assertEqual(res["status"], "error")


    # ==========================
    # 3. OmniNlpArchitectEngine (10 tests)
    # ==========================
    def setUp_nlp(self):
        return OmniNlpArchitectEngine()

    def test_nlp_diagnostics(self):
        eng = self.setUp_nlp()
        self.assertEqual(eng.diagnostics()["status"], "operational")

    def test_nlp_provision_success(self):
        eng = self.setUp_nlp()
        res = eng.provision_nlp_topology("NER")
        self.assertEqual(res["status"], "success")

    def test_nlp_provision_invalid(self):
        eng = self.setUp_nlp()
        res = eng.provision_nlp_topology("MAGIC")
        self.assertEqual(res["status"], "error")

    def test_nlp_extract_ner(self):
        eng = self.setUp_nlp()
        pid = eng.provision_nlp_topology("NER")["pipeline_id"]
        res = eng.extract_semantics(pid, "OMNI is working")
        self.assertEqual(res["status"], "success")
        self.assertTrue("entities" in res["semantics"])

    def test_nlp_extract_intent(self):
        eng = self.setUp_nlp()
        pid = eng.provision_nlp_topology("INTENT")["pipeline_id"]
        res = eng.extract_semantics(pid, "Run program")
        self.assertEqual(res["status"], "success")
        self.assertTrue("intent" in res["semantics"])

    def test_nlp_extract_missing(self):
        eng = self.setUp_nlp()
        res = eng.extract_semantics("missing", "text")
        self.assertEqual(res["status"], "error")

    def test_nlp_extract_empty(self):
        eng = self.setUp_nlp()
        pid = eng.provision_nlp_topology("NER")["pipeline_id"]
        res = eng.extract_semantics(pid, "   ")
        self.assertEqual(res["status"], "error")

    def test_nlp_density_success(self):
        eng = self.setUp_nlp()
        res = eng.calculate_lexical_density("one two three one")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["lexical_density"], 0.75) # 3 unique / 4 total

    def test_nlp_density_empty(self):
        eng = self.setUp_nlp()
        res = eng.calculate_lexical_density("")
        self.assertEqual(res["status"], "error")

    def test_nlp_config_format(self):
        eng = self.setUp_nlp()
        res = eng.provision_nlp_topology("PARSING")
        self.assertEqual(res["config"]["quantization"], "BF16")


    # ==========================
    # 4. OmniUltralyticsProEngine (10 tests)
    # ==========================
    def setUp_upro(self):
        return OmniUltralyticsProEngine()

    def test_upro_diagnostics(self):
        eng = self.setUp_upro()
        self.assertEqual(eng.diagnostics()["status"], "operational")

    def test_upro_mount_success(self):
        eng = self.setUp_upro()
        res = eng.mount_vision_weights("yolov8n", "detect")
        self.assertEqual(res["status"], "success")

    def test_upro_mount_invalid_task(self):
        eng = self.setUp_upro()
        res = eng.mount_vision_weights("yolov8n", "fly")
        self.assertEqual(res["status"], "error")

    def test_upro_mount_invalid_variant(self):
        eng = self.setUp_upro()
        res = eng.mount_vision_weights("resnet", "detect")
        self.assertEqual(res["status"], "error")

    def test_upro_inference_success(self):
        eng = self.setUp_upro()
        mid = eng.mount_vision_weights("yolov8n")["model_id"]
        res = eng.run_spatial_detection(mid, (224, 224, 3))
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["detections_count"], 2)

    def test_upro_inference_invalid_tensor(self):
        eng = self.setUp_upro()
        mid = eng.mount_vision_weights("yolov8n")["model_id"]
        res = eng.run_spatial_detection(mid, (224, 224)) # missing channels
        self.assertEqual(res["status"], "error")

    def test_upro_inference_invalid_conf(self):
        eng = self.setUp_upro()
        mid = eng.mount_vision_weights("yolov8n")["model_id"]
        res = eng.run_spatial_detection(mid, (224, 224, 3), 1.5)
        self.assertEqual(res["status"], "error")

    def test_upro_compile_trt_success(self):
        eng = self.setUp_upro()
        mid = eng.mount_vision_weights("yolov8n")["model_id"]
        res = eng.compile_tensorrt_engine(mid, True)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["precision_mode"], "FP16")

    def test_upro_compile_trt_fp32(self):
        eng = self.setUp_upro()
        mid = eng.mount_vision_weights("yolov8n")["model_id"]
        res = eng.compile_tensorrt_engine(mid, False)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["precision_mode"], "FP32")

    def test_upro_compile_missing(self):
        eng = self.setUp_upro()
        res = eng.compile_tensorrt_engine("missing")
        self.assertEqual(res["status"], "error")


    # ==========================
    # 5. OmniAwesomeMlssEngine (10 tests)
    # ==========================
    def setUp_mlss(self):
        return OmniAwesomeMlssEngine()

    def test_mlss_diagnostics(self):
        eng = self.setUp_mlss()
        self.assertEqual(eng.diagnostics()["status"], "operational")

    def test_mlss_index_success(self):
        eng = self.setUp_mlss()
        res = eng.index_curriculum_domain("RL", ["Q-Learning", "PPO"])
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["indexed_concepts"], 2)

    def test_mlss_index_empty_name(self):
        eng = self.setUp_mlss()
        res = eng.index_curriculum_domain("", ["PPO"])
        self.assertEqual(res["status"], "error")

    def test_mlss_index_empty_concepts(self):
        eng = self.setUp_mlss()
        res = eng.index_curriculum_domain("RL", [])
        self.assertEqual(res["status"], "error")

    def test_mlss_query_success(self):
        eng = self.setUp_mlss()
        eng.index_curriculum_domain("RL", ["Q-Learning", "PPO"])
        res = eng.query_semantic_pathway("PPO")
        self.assertEqual(res["status"], "success")
        self.assertTrue("RL" in res["results"])

    def test_mlss_query_no_result(self):
        eng = self.setUp_mlss()
        eng.index_curriculum_domain("RL", ["Q-Learning"])
        res = eng.query_semantic_pathway("GAN")
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["results"]), 0)

    def test_mlss_query_empty_graph(self):
        eng = self.setUp_mlss()
        res = eng.query_semantic_pathway("GAN")
        self.assertEqual(res["status"], "error")

    def test_mlss_query_empty_query(self):
        eng = self.setUp_mlss()
        eng.index_curriculum_domain("RL", ["Q-Learning"])
        res = eng.query_semantic_pathway("")
        self.assertEqual(res["status"], "error")

    def test_mlss_metrics_success(self):
        eng = self.setUp_mlss()
        eng.index_curriculum_domain("RL", ["A", "B"])
        eng.index_curriculum_domain("CV", ["C", "D", "E"])
        res = eng.synthesize_global_graph_metrics()
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["metrics"]["active_domains"], 2)
        self.assertEqual(res["metrics"]["hyper_nodes"], 5)

    def test_mlss_metrics_density(self):
        eng = self.setUp_mlss()
        eng.index_curriculum_domain("RL", ["A", "B"])
        res = eng.synthesize_global_graph_metrics()
        self.assertEqual(res["metrics"]["graph_density"], 2.0)


if __name__ == "__main__":
    unittest.main()
