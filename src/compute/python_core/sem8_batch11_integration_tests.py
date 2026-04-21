"""
Semester 8 Batch 11 — Integration Tests

Validates all 5 Batch 11 engines using real library calls.
"""

import asyncio
import unittest

from omni_orange3_engine import OmniOrange3Engine
from omni_strands_agents_engine import OmniStrandsAgentsEngine
from omni_keras_rl_engine import OmniKerasRlEngine
from omni_daft_engine import OmniDaftEngine
from omni_ltp_engine import OmniLtpEngine


class TestSem8Batch11Engines(unittest.IsolatedAsyncioTestCase):
    """Integration tests for Semester 8 Batch 11 engines."""

    # ── Orange3 ──────────────────────────────────────────────────────

    async def test_orange3_initialization(self) -> None:
        """Orange3 engine must initialize with native Table/Domain."""
        engine = OmniOrange3Engine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")

    async def test_orange3_process(self) -> None:
        """Orange3 engine must run real CrossValidation pipeline."""
        engine = OmniOrange3Engine()
        await engine.initialize()
        res = await engine.process({
            "num_samples": 200,
            "num_features": 4,
            "num_folds": 3,
        })
        self.assertEqual(res["status"], "success")
        data = res["data"]["orange3_pipeline_result"]
        self.assertEqual(data["num_samples"], 200)
        self.assertIn("RandomForest", data["results"])
        self.assertGreater(data["results"]["RandomForest"]["CA"], 0.0)

    async def test_orange3_diagnostics(self) -> None:
        """Orange3 diagnostics must report active."""
        engine = OmniOrange3Engine()
        await engine.initialize()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "active")

    # ── Strands Agents ───────────────────────────────────────────────

    async def test_strands_initialization(self) -> None:
        """Strands engine must initialize with SDK type validation."""
        engine = OmniStrandsAgentsEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")

    async def test_strands_message_assembly(self) -> None:
        """Strands engine must assemble a real message sequence."""
        engine = OmniStrandsAgentsEngine()
        await engine.initialize()
        res = await engine.process({
            "mode": "message_assembly",
            "num_turns": 3,
            "system_prompt": "You are OMNI.",
        })
        self.assertEqual(res["status"], "success")
        data = res["data"]["strands_agents_result"]
        self.assertEqual(data["num_turns_assembled"], 3)
        self.assertEqual(data["total_messages"], 6)

    async def test_strands_tool_registration(self) -> None:
        """Strands engine must register tool specs."""
        engine = OmniStrandsAgentsEngine()
        await engine.initialize()
        res = await engine.process({
            "mode": "tool_registration",
            "tool_names": ["search", "calc", "code_exec"],
        })
        self.assertEqual(res["status"], "success")
        data = res["data"]["strands_agents_result"]
        self.assertEqual(data["registered_tool_count"], 3)
        self.assertTrue(data["schema_valid"])

    # ── Keras-RL ─────────────────────────────────────────────────────

    async def test_keras_rl_initialization(self) -> None:
        """Keras-RL engine must initialize successfully."""
        engine = OmniKerasRlEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")

    async def test_keras_rl_process(self) -> None:
        """Keras-RL engine must execute RL training."""
        engine = OmniKerasRlEngine()
        await engine.initialize()
        res = await engine.process({
            "num_episodes": 50,
            "num_states": 8,
            "num_actions": 4,
        })
        self.assertEqual(res["status"], "success")
        data = res["data"]["keras_rl_result"]
        self.assertIn("q_table_shape", data)
        self.assertIsInstance(data["mean_reward"], float)

    # ── Daft ─────────────────────────────────────────────────────────

    async def test_daft_initialization(self) -> None:
        """Daft engine must initialize with native DataFrame."""
        engine = OmniDaftEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")

    async def test_daft_process(self) -> None:
        """Daft engine must execute a real DataFrame pipeline."""
        engine = OmniDaftEngine()
        await engine.initialize()
        res = await engine.process({"num_rows": 200, "num_cols": 3})
        self.assertEqual(res["status"], "success")
        data = res["data"]["daft_pipeline_result"]
        self.assertEqual(data["num_rows"], 200)
        self.assertIn("col_sum", data["columns"])
        self.assertGreater(data["aggregation_groups"], 0)

    # ── LTP ──────────────────────────────────────────────────────────

    async def test_ltp_initialization(self) -> None:
        """LTP engine must initialize successfully."""
        engine = OmniLtpEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")

    async def test_ltp_process_cws(self) -> None:
        """LTP engine must segment Chinese text."""
        engine = OmniLtpEngine()
        await engine.initialize()
        res = await engine.process({
            "texts": ["中国科学技术大学是一所优秀的大学。"],
            "tasks": ["cws"],
        })
        self.assertEqual(res["status"], "success")
        data = res["data"]["ltp_pipeline_result"]
        self.assertIn("cws", data["results"])
        self.assertGreater(len(data["results"]["cws"][0]), 0)

    async def test_ltp_process_cws_pos(self) -> None:
        """LTP engine must segment and POS-tag Chinese text."""
        engine = OmniLtpEngine()
        await engine.initialize()
        res = await engine.process({
            "texts": ["自然语言处理是人工智能的重要领域。"],
            "tasks": ["cws", "pos"],
        })
        self.assertEqual(res["status"], "success")
        data = res["data"]["ltp_pipeline_result"]
        self.assertIn("cws", data["results"])
        self.assertIn("pos", data["results"])
        self.assertEqual(
            len(data["results"]["cws"][0]),
            len(data["results"]["pos"][0]),
        )


if __name__ == "__main__":
    unittest.main()
