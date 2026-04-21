"""
Semester 8 Batch 10 — Integration Tests

Validates all 5 Batch 10 engines using real library calls.
"""

import asyncio
import unittest

from omni_snorkel_engine import OmniSnorkelEngine
from omni_gorgonia_engine import OmniGorgoniaEngine
from omni_river_engine import OmniRiverEngine
from omni_causalml_engine import OmniCausalmlEngine
from omni_nn_svg_engine import OmniNnSvgEngine


class TestSem8Batch10Engines(unittest.IsolatedAsyncioTestCase):
    """Integration tests for Semester 8 Batch 10 engines."""

    # ── Snorkel ──────────────────────────────────────────────────────

    async def test_snorkel_initialization(self) -> None:
        """Snorkel engine must initialize with native LFs."""
        engine = OmniSnorkelEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")

    async def test_snorkel_process(self) -> None:
        """Snorkel engine must run a full LabelModel pipeline."""
        engine = OmniSnorkelEngine()
        await engine.initialize()
        res = await engine.process({"num_samples": 200, "num_epochs": 50})
        self.assertEqual(res["status"], "success")
        data = res["data"]["snorkel_pipeline_result"]
        self.assertEqual(data["num_samples"], 200)
        self.assertEqual(data["num_lfs_applied"], 4)
        self.assertIsInstance(data["mean_positive_probability"], float)

    async def test_snorkel_diagnostics(self) -> None:
        """Snorkel diagnostics must report active status after init."""
        engine = OmniSnorkelEngine()
        await engine.initialize()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "active")
        self.assertEqual(diag["registered_lf_count"], 4)

    # ── Gorgonia ─────────────────────────────────────────────────────

    async def test_gorgonia_initialization(self) -> None:
        """Gorgonia engine must initialize successfully."""
        engine = OmniGorgoniaEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")

    async def test_gorgonia_process(self) -> None:
        """Gorgonia engine must compute real scalar + tensor ops."""
        engine = OmniGorgoniaEngine()
        await engine.initialize()
        res = await engine.process({"a": 3.0, "b": 4.0, "tensor_rows": 3})
        self.assertEqual(res["status"], "success")
        data = res["data"]["gorgonia_computation"]
        self.assertAlmostEqual(data["sum"], 7.0)
        self.assertAlmostEqual(data["product"], 12.0)
        self.assertEqual(data["sq_shape"], [3, 3])

    # ── River ────────────────────────────────────────────────────────

    async def test_river_initialization(self) -> None:
        """River engine must initialize with a working pipeline."""
        engine = OmniRiverEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")

    async def test_river_process_synthetic(self) -> None:
        """River engine must stream synthetic data through HoeffdingTree."""
        engine = OmniRiverEngine()
        await engine.initialize()
        res = await engine.process({"num_samples": 500, "num_features": 5})
        self.assertEqual(res["status"], "success")
        data = res["data"]["river_streaming_result"]
        self.assertEqual(data["num_samples_streamed"], 500)
        self.assertGreater(data["final_accuracy"], 0.0)

    async def test_river_process_builtin(self) -> None:
        """River engine must train on the built-in Phishing dataset."""
        engine = OmniRiverEngine()
        await engine.initialize()
        res = await engine.process({"use_builtin_dataset": True})
        self.assertEqual(res["status"], "success")
        data = res["data"]["river_streaming_result"]
        self.assertIn("Phishing", data["dataset"])
        self.assertGreater(data["samples_processed"], 0)

    # ── CausalML ─────────────────────────────────────────────────────

    async def test_causalml_initialization(self) -> None:
        """CausalML engine must initialize with synthetic data check."""
        engine = OmniCausalmlEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")

    async def test_causalml_process_s_learner(self) -> None:
        """CausalML S-Learner must estimate ATE from real data."""
        engine = OmniCausalmlEngine()
        await engine.initialize()
        res = await engine.process({
            "num_samples": 300,
            "num_features": 5,
            "learner_type": "s",
        })
        self.assertEqual(res["status"], "success")
        data = res["data"]["causalml_uplift_result"]
        self.assertEqual(data["learner_type"], "S-Learner")
        self.assertIsInstance(data["ate_estimate"], float)

    async def test_causalml_process_t_learner(self) -> None:
        """CausalML T-Learner must estimate ATE from real data."""
        engine = OmniCausalmlEngine()
        await engine.initialize()
        res = await engine.process({
            "num_samples": 300,
            "num_features": 5,
            "learner_type": "t",
        })
        self.assertEqual(res["status"], "success")
        data = res["data"]["causalml_uplift_result"]
        self.assertEqual(data["learner_type"], "T-Learner")
        self.assertIsInstance(data["ate_estimate"], float)

    # ── NN-SVG ───────────────────────────────────────────────────────

    async def test_nn_svg_initialization(self) -> None:
        """NN-SVG engine must initialize with SVG smoke-test."""
        engine = OmniNnSvgEngine()
        result = await engine.initialize()
        self.assertEqual(result["status"], "success")

    async def test_nn_svg_process_fcnn(self) -> None:
        """NN-SVG engine must generate valid FCNN SVG markup."""
        engine = OmniNnSvgEngine()
        await engine.initialize()
        res = await engine.process({
            "architecture": "fcnn",
            "layers": [784, 128, 64, 10],
        })
        self.assertEqual(res["status"], "success")
        data = res["data"]["nn_svg_result"]
        self.assertTrue(data["svg_valid"])
        self.assertEqual(data["architecture"], "fcnn")
        self.assertGreater(data["svg_element_counts"]["circles"], 0)
        self.assertGreater(data["svg_element_counts"]["lines"], 0)

    async def test_nn_svg_process_cnn(self) -> None:
        """NN-SVG engine must generate valid CNN SVG markup."""
        engine = OmniNnSvgEngine()
        await engine.initialize()
        res = await engine.process({
            "architecture": "cnn",
            "layers": [1, 6, 16, 120],
        })
        self.assertEqual(res["status"], "success")
        data = res["data"]["nn_svg_result"]
        self.assertTrue(data["svg_valid"])
        self.assertEqual(data["architecture"], "cnn")
        self.assertGreater(data["svg_element_counts"]["rects"], 0)


if __name__ == "__main__":
    unittest.main()
