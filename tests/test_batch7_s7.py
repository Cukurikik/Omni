# -*- coding: utf-8 -*-
"""
OMNI SEMESTER 7 — BATCH 7 INTEGRATION TESTS
Validating 5 New Omni Engines against Zero-Mock Monadic constraints.
Contains 50 comprehensive unit tests (10 per engine).
"""

import unittest
from src.compute.python_core.system.omni_nesa_engine import OmniNesaEngine
from src.compute.python_core.system.omni_tencent_ml_images_engine import OmniTencentMLImagesEngine
from src.compute.python_core.system.omni_webdataset_engine import OmniWebDatasetEngine
from src.compute.python_core.system.omni_spotlight_engine import OmniSpotlightEngine
from src.compute.python_core.system.omni_lc0_engine import OmniLc0Engine

class TestBatch7Semester7(unittest.TestCase):
    
    # ==========================
    # 1. OmniNesaEngine (10 tests)
    # ==========================
    def setUp_nesa(self):
        return OmniNesaEngine()

    def test_nesa_diagnostics(self):
        eng = self.setUp_nesa()
        diag = eng.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_nesa_initialize_node_success(self):
        eng = self.setUp_nesa()
        res = eng.initialize_nesa_node("node_1", "A100")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["node_info"]["hardware"], "A100")

    def test_nesa_initialize_node_duplicate(self):
        eng = self.setUp_nesa()
        eng.initialize_nesa_node("node_1")
        res = eng.initialize_nesa_node("node_1")
        self.assertEqual(res["status"], "error")

    def test_nesa_deploy_task_success(self):
        eng = self.setUp_nesa()
        eng.initialize_nesa_node("node_1")
        res = eng.deploy_inference_task("llama_3", 10.5)
        self.assertEqual(res["status"], "success")
        self.assertTrue("task_id" in res)
        self.assertEqual(res["assignment"]["assigned_node"], "node_1")

    def test_nesa_deploy_task_no_nodes(self):
        eng = self.setUp_nesa()
        res = eng.deploy_inference_task("llama_3", 10.5)
        self.assertEqual(res["status"], "error")

    def test_nesa_deploy_task_invalid_payload(self):
        eng = self.setUp_nesa()
        eng.initialize_nesa_node("node_1")
        res = eng.deploy_inference_task("llama_3", -5.0)
        self.assertEqual(res["status"], "error")

    def test_nesa_verify_consensus_success(self):
        eng = self.setUp_nesa()
        eng.initialize_nesa_node("node_1")
        task = eng.deploy_inference_task("llama_3", 10.5)
        res = eng.verify_consensus(task["task_id"])
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["consensus_reached"])
        self.assertEqual(res["node_reputation_updated"], 101.5)

    def test_nesa_verify_consensus_missing_task(self):
        eng = self.setUp_nesa()
        res = eng.verify_consensus("missing_task")
        self.assertEqual(res["status"], "error")

    def test_nesa_verify_consensus_already_verified(self):
        eng = self.setUp_nesa()
        eng.initialize_nesa_node("node_1")
        task = eng.deploy_inference_task("llama_3", 10.5)
        eng.verify_consensus(task["task_id"])
        res = eng.verify_consensus(task["task_id"])
        self.assertEqual(res["status"], "success") # returns already verified msg
        self.assertEqual(res["message"], "Task already verified.")

    def test_nesa_node_tasks_count(self):
        eng = self.setUp_nesa()
        eng.initialize_nesa_node("node_1")
        eng.deploy_inference_task("llama_3", 10.5)
        eng.deploy_inference_task("llama_3", 5.5)
        self.assertEqual(eng.nodes["node_1"]["tasks_completed"], 2)


    # ==========================
    # 2. OmniTencentMLImagesEngine (10 tests)
    # ==========================
    def setUp_tencent(self):
        return OmniTencentMLImagesEngine()

    def test_tencent_diagnostics(self):
        eng = self.setUp_tencent()
        self.assertEqual(eng.diagnostics()["status"], "operational")

    def test_tencent_load_taxonomy_success(self):
        eng = self.setUp_tencent()
        res = eng.load_taxonomy({"L1": "dog", "L2": "cat"})
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["taxonomy_size"], 2)

    def test_tencent_load_taxonomy_empty(self):
        eng = self.setUp_tencent()
        res = eng.load_taxonomy({})
        self.assertEqual(res["status"], "error")

    def test_tencent_config_model_success(self):
        eng = self.setUp_tencent()
        eng.load_taxonomy({"L1": "dog", "L2": "cat"})
        res = eng.configure_resnet101_multilabel("r101")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["model_config"]["output_dim"], 2)

    def test_tencent_config_model_no_taxonomy(self):
        eng = self.setUp_tencent()
        res = eng.configure_resnet101_multilabel("r101")
        self.assertEqual(res["status"], "error")

    def test_tencent_config_model_duplicate(self):
        eng = self.setUp_tencent()
        eng.load_taxonomy({"L1": "dog"})
        eng.configure_resnet101_multilabel("r101")
        res = eng.configure_resnet101_multilabel("r101")
        self.assertEqual(res["status"], "error")

    def test_tencent_predict_success(self):
        eng = self.setUp_tencent()
        eng.load_taxonomy({"L1": "dog", "L2": "cat", "L3": "bird"})
        eng.configure_resnet101_multilabel("r101")
        res = eng.predict_image_tags("r101", (224, 224, 3))
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["predictions"]), 3)

    def test_tencent_predict_missing_model(self):
        eng = self.setUp_tencent()
        res = eng.predict_image_tags("missing", (224, 224, 3))
        self.assertEqual(res["status"], "error")

    def test_tencent_predict_invalid_shape(self):
        eng = self.setUp_tencent()
        eng.load_taxonomy({"L1": "dog"})
        eng.configure_resnet101_multilabel("r101")
        res = eng.predict_image_tags("r101", (224, 224)) # 2D
        self.assertEqual(res["status"], "error")

    def test_tencent_predict_grayscale_channels(self):
        eng = self.setUp_tencent()
        eng.load_taxonomy({"L1": "dog"})
        eng.configure_resnet101_multilabel("r101")
        res = eng.predict_image_tags("r101", (224, 224, 1))
        self.assertEqual(res["status"], "error")


    # ==========================
    # 3. OmniWebDatasetEngine (10 tests)
    # ==========================
    def setUp_webdataset(self):
        return OmniWebDatasetEngine()

    def test_wds_diagnostics(self):
        eng = self.setUp_webdataset()
        self.assertEqual(eng.diagnostics()["status"], "operational")

    def test_wds_create_writer_success(self):
        eng = self.setUp_webdataset()
        res = eng.create_tar_shard_writer("shard-%06d.tar")
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["writer_id"].startswith("wds_writer_"))

    def test_wds_create_writer_invalid_count(self):
        eng = self.setUp_webdataset()
        res = eng.create_tar_shard_writer("shard-%06d.tar", max_count=0)
        self.assertEqual(res["status"], "error")

    def test_wds_config_pipeline_success(self):
        eng = self.setUp_webdataset()
        res = eng.configure_decode_pipeline("pipe_1", ["pil", "torch", "json"])
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["chain"]), 3)

    def test_wds_config_pipeline_invalid_decoder(self):
        eng = self.setUp_webdataset()
        res = eng.configure_decode_pipeline("pipe_1", ["pil", "magic_decoder"])
        self.assertEqual(res["status"], "error")

    def test_wds_iterate_success(self):
        eng = self.setUp_webdataset()
        w = eng.create_tar_shard_writer("shard-%06d.tar")["writer_id"]
        eng.configure_decode_pipeline("pipe_1", ["json", "torch"])
        res = eng.iterate_shard(w, "pipe_1", 5)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["batch_size"], 5)
        self.assertTrue("tensor.pth" in res["samples"][0])

    def test_wds_iterate_missing_writer(self):
        eng = self.setUp_webdataset()
        eng.configure_decode_pipeline("pipe_1", ["pil"])
        res = eng.iterate_shard("missing_writer", "pipe_1", 5)
        self.assertEqual(res["status"], "error")

    def test_wds_iterate_missing_pipeline(self):
        eng = self.setUp_webdataset()
        w = eng.create_tar_shard_writer("shard.tar")["writer_id"]
        res = eng.iterate_shard(w, "missing", 5)
        self.assertEqual(res["status"], "error")

    def test_wds_iterate_zero_records(self):
        eng = self.setUp_webdataset()
        w = eng.create_tar_shard_writer("shard.tar")["writer_id"]
        eng.configure_decode_pipeline("pipe_1", ["pil"])
        res = eng.iterate_shard(w, "pipe_1", -1)
        self.assertEqual(res["status"], "error")

    def test_wds_writer_metrics_update(self):
        eng = self.setUp_webdataset()
        w = eng.create_tar_shard_writer("shard.tar")["writer_id"]
        eng.configure_decode_pipeline("pipe_1", ["pil"])
        eng.iterate_shard(w, "pipe_1", 10)
        self.assertEqual(eng.shards[w]["current_count"], 10)
        self.assertEqual(eng.shards[w]["bytes_written"], 10240)


    # ==========================
    # 4. OmniSpotlightEngine (10 tests)
    # ==========================
    def setUp_spotlight(self):
        return OmniSpotlightEngine()

    def test_spotlight_diagnostics(self):
        eng = self.setUp_spotlight()
        self.assertEqual(eng.diagnostics()["status"], "operational")

    def test_spotlight_build_success(self):
        eng = self.setUp_spotlight()
        res = eng.build_implicit_factorization("m1", 64, "bpr")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["config"]["embedding_dim"], 64)

    def test_spotlight_build_duplicate(self):
        eng = self.setUp_spotlight()
        eng.build_implicit_factorization("m1")
        res = eng.build_implicit_factorization("m1")
        self.assertEqual(res["status"], "error")

    def test_spotlight_build_invalid_loss(self):
        eng = self.setUp_spotlight()
        res = eng.build_implicit_factorization("m1", loss="magic")
        self.assertEqual(res["status"], "error")

    def test_spotlight_fit_success(self):
        eng = self.setUp_spotlight()
        eng.build_implicit_factorization("m1")
        res = eng.fit_interactions("m1", 100, 1000, 50000)
        self.assertEqual(res["status"], "success")
        self.assertTrue(res["fitted_state"])

    def test_spotlight_fit_missing_model(self):
        eng = self.setUp_spotlight()
        res = eng.fit_interactions("m1", 100, 1000, 5000)
        self.assertEqual(res["status"], "error")

    def test_spotlight_fit_invalid_counts(self):
        eng = self.setUp_spotlight()
        eng.build_implicit_factorization("m1")
        res = eng.fit_interactions("m1", -1, 100, 100)
        self.assertEqual(res["status"], "error")

    def test_spotlight_predict_success(self):
        eng = self.setUp_spotlight()
        eng.build_implicit_factorization("m1")
        eng.fit_interactions("m1", 10, 100, 500)
        res = eng.predict_recommendations("m1", user_id=5, top_k=3)
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["recommendations"]), 3)

    def test_spotlight_predict_unfitted(self):
        eng = self.setUp_spotlight()
        eng.build_implicit_factorization("m1")
        res = eng.predict_recommendations("m1", 0)
        self.assertEqual(res["status"], "error")

    def test_spotlight_predict_out_of_bounds_user(self):
        eng = self.setUp_spotlight()
        eng.build_implicit_factorization("m1")
        eng.fit_interactions("m1", 5, 10, 100)
        res = eng.predict_recommendations("m1", user_id=10) # max is 4
        self.assertEqual(res["status"], "error")


    # ==========================
    # 5. OmniLc0Engine (10 tests)
    # ==========================
    def setUp_lc0(self):
        return OmniLc0Engine()

    def test_lc0_diagnostics(self):
        eng = self.setUp_lc0()
        self.assertEqual(eng.diagnostics()["status"], "operational")

    def test_lc0_initialize_success(self):
        eng = self.setUp_lc0()
        res = eng.initialize_mcts_search("inst_1", nodes=1000)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["instance"]["mcts_nodes"], 1000)

    def test_lc0_initialize_duplicate(self):
        eng = self.setUp_lc0()
        eng.initialize_mcts_search("inst_1")
        res = eng.initialize_mcts_search("inst_1")
        self.assertEqual(res["status"], "error")

    def test_lc0_initialize_invalid_nodes(self):
        eng = self.setUp_lc0()
        res = eng.initialize_mcts_search("inst_1", nodes=0)
        self.assertEqual(res["status"], "error")

    def test_lc0_eval_success(self):
        eng = self.setUp_lc0()
        eng.initialize_mcts_search("inst_1")
        res = eng.evaluate_board_fen("inst_1", "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["q_value"], 0.55)

    def test_lc0_eval_black(self):
        eng = self.setUp_lc0()
        eng.initialize_mcts_search("inst_1")
        res = eng.evaluate_board_fen("inst_1", "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["q_value"], -0.55)

    def test_lc0_eval_missing_inst(self):
        eng = self.setUp_lc0()
        res = eng.evaluate_board_fen("missing", "fen string is here 1")
        self.assertEqual(res["status"], "error")

    def test_lc0_eval_invalid_fen(self):
        eng = self.setUp_lc0()
        eng.initialize_mcts_search("inst_1")
        res = eng.evaluate_board_fen("inst_1", "invalidfen")
        self.assertEqual(res["status"], "error")

    def test_lc0_query_success(self):
        eng = self.setUp_lc0()
        eng.initialize_mcts_search("inst_1")
        res = eng.query_best_move("inst_1")
        self.assertEqual(res["status"], "success")
        self.assertTrue("best_move" in res)
        self.assertEqual(res["best_move"], "e2e4") # Default initial fen move

    def test_lc0_query_missing_inst(self):
        eng = self.setUp_lc0()
        res = eng.query_best_move("missing")
        self.assertEqual(res["status"], "error")

if __name__ == "__main__":
    unittest.main()
