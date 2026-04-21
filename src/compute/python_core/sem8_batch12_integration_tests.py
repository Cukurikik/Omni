"""
Semester 8 Batch 12 — Integration Tests

Validates all 5 Batch 12 engines:
  1. OmniZenMLEngine          (zenml-io/zenml)
  2. OmniSAHIEngine           (obss/sahi)
  3. OmniAugmentorEngine      (mdbloice/Augmentor)
  4. OmniAIDataSciTeamEngine  (business-science/ai-data-science-team)
  5. OmniSynapseMLEngine      (microsoft/SynapseML)

All tests use real algorithmic logic — zero mock, zero simulation.

Note: Each engine defines its own Ok/Err monadic types. Tests validate
using duck-typing (hasattr 'value' / 'error') to respect cross-module
type identity without coupling.
"""

import unittest
import numpy as np

from omni_zenml_engine import (
    OmniZenMLEngine, step, pipeline, PipelineStep,
)
from omni_sahi_engine import OmniSAHIEngine
from omni_augmentor_engine import OmniAugmentorEngine
from omni_synapse_ml_engine import OmniSynapseMLEngine
from omni_ai_datasci_team_engine import (
    OmniAIDataSciTeamEngine, PipelineStep as DSPipelineStep,
)


# ---------------------------------------------------------------------------
# Monadic duck-type helpers
# ---------------------------------------------------------------------------

def is_ok(result) -> bool:
    """Check if a Result is Ok by structural typing (duck-type)."""
    return hasattr(result, "value") and not hasattr(result, "error")


def is_err(result) -> bool:
    """Check if a Result is Err by structural typing (duck-type)."""
    return hasattr(result, "error") and not hasattr(result, "value")


def unwrap(result):
    """Extract the value from an Ok result."""
    return result.value


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------

class TestZenMLEngine(unittest.TestCase):
    """Integration tests for ZenML MLOps orchestration engine."""

    def test_zenml_diagnostics(self) -> None:
        """ZenML diagnostics must report operational."""
        engine = OmniZenMLEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")
        self.assertIn("ArtifactStore", diag["components"])

    def test_zenml_artifact_store(self) -> None:
        """ZenML artifact store must save and retrieve versioned artifacts."""
        engine = OmniZenMLEngine()
        art = engine.artifact_store.save("test_data", [1, 2, 3], "Dataset")
        self.assertEqual(art.version, 1)
        self.assertEqual(art.name, "test_data")

        loaded = engine.get_artifact("test_data")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.data, [1, 2, 3])

    def test_zenml_pipeline_execution(self) -> None:
        """ZenML must execute a full DAG pipeline and track the run."""
        engine = OmniZenMLEngine()

        @step(name="load_data")
        def load_data():
            return np.array([1.0, 2.0, 3.0, 4.0, 5.0])

        @step(name="compute_mean")
        def compute_mean(data):
            return float(np.mean(data))

        @pipeline(name="stat_pipeline")
        def stat_pipeline():
            data = load_data()
            mean_val = compute_mean(data)
            return (mean_val,)

        result = engine.execute(stat_pipeline())
        self.assertTrue(is_ok(result))

        run = unwrap(result)
        self.assertEqual(run.status, "completed")
        self.assertGreater(len(run.artifacts_produced), 0)

    def test_zenml_step_decorator(self) -> None:
        """ZenML step decorator must produce PipelineStep instances."""
        @step(name="my_step")
        def dummy():
            return 42

        self.assertIsInstance(dummy, PipelineStep)
        self.assertEqual(dummy.name, "my_step")


class TestSAHIEngine(unittest.TestCase):
    """Integration tests for SAHI sliced inference engine."""

    def test_sahi_diagnostics(self) -> None:
        """SAHI diagnostics must report operational."""
        engine = OmniSAHIEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_sahi_slice_calculation(self) -> None:
        """SAHI must compute overlapping slices for a large image."""
        engine = OmniSAHIEngine()
        slicer = engine.create_slicer(slice_height=512, slice_width=512, overlap_h=0.2, overlap_w=0.2)
        result = slicer.calculate_slices(2048, 2048)
        self.assertTrue(is_ok(result))
        slices = unwrap(result)
        self.assertGreater(len(slices), 1)

        # Every slice must have valid coordinates
        for s in slices:
            self.assertGreaterEqual(s.xmin, 0)
            self.assertGreaterEqual(s.ymin, 0)
            self.assertLessEqual(s.xmax, 2048)
            self.assertLessEqual(s.ymax, 2048)

    def test_sahi_single_slice_for_small_image(self) -> None:
        """SAHI must return a single slice when image is smaller than slice size."""
        engine = OmniSAHIEngine()
        slicer = engine.create_slicer(slice_height=512, slice_width=512)
        result = slicer.calculate_slices(256, 256)
        self.assertTrue(is_ok(result))
        self.assertEqual(len(unwrap(result)), 1)

    def test_sahi_projection(self) -> None:
        """SAHI prediction combiner must project boxes to parent coords."""
        engine = OmniSAHIEngine()
        combiner = engine.get_combiner()
        boxes = np.array([[10.0, 20.0, 50.0, 60.0]], dtype=np.float32)
        result = combiner.project_to_parent(boxes, shift_xy=(100, 200))
        self.assertTrue(is_ok(result))
        projected = unwrap(result)
        np.testing.assert_array_almost_equal(projected, [[110.0, 220.0, 150.0, 260.0]])


class TestAugmentorEngine(unittest.TestCase):
    """Integration tests for Augmentor stochastic pipeline engine."""

    def test_augmentor_diagnostics(self) -> None:
        """Augmentor diagnostics must report operational."""
        engine = OmniAugmentorEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")

    def test_augmentor_rotate90(self) -> None:
        """Augmentor must apply 90-degree rotation to a numpy image."""
        engine = OmniAugmentorEngine()
        pipe = engine.create_pipeline()
        result = pipe.add_rotate_90(probability=1.0)
        self.assertTrue(is_ok(result))

        img = np.random.randint(0, 255, (64, 128, 3), dtype=np.uint8)
        res = pipe.process_image(img)
        self.assertTrue(is_ok(res))
        output = unwrap(res)
        rotated = output["image"]
        self.assertEqual(rotated.shape, (128, 64, 3))
        self.assertIn("Rotate90", output["applied_operations"])

    def test_augmentor_flip_lr(self) -> None:
        """Augmentor must flip an image left-right."""
        engine = OmniAugmentorEngine()
        pipe = engine.create_pipeline()
        pipe.add_flip_left_right(probability=1.0)

        img = np.arange(12).reshape(3, 4, 1)
        res = pipe.process_image(img)
        self.assertTrue(is_ok(res))
        flipped = unwrap(res)["image"]
        np.testing.assert_array_equal(flipped[:, 0, 0], img[:, -1, 0])

    def test_augmentor_pipeline_chaining(self) -> None:
        """Augmentor must chain multiple operations and apply based on probability."""
        engine = OmniAugmentorEngine()
        pipe = engine.create_pipeline()
        pipe.add_rotate_90(probability=1.0)
        pipe.add_flip_left_right(probability=1.0)

        img = np.random.randint(0, 255, (64, 128, 3), dtype=np.uint8)
        res = pipe.process_image(img)
        self.assertTrue(is_ok(res))
        self.assertEqual(len(unwrap(res)["applied_operations"]), 2)


class TestAIDataSciTeamEngine(unittest.TestCase):
    """Integration tests for AI Data Science Team multi-agent engine."""

    def _make_dataset(self) -> dict:
        """Helper to create a synthetic dataset."""
        np.random.seed(42)
        return {
            "age": np.random.randint(18, 70, 100).astype(float),
            "income": np.random.uniform(20000, 150000, 100),
            "score": np.random.uniform(0, 100, 100),
        }

    def test_datasci_diagnostics(self) -> None:
        """AI DS Team diagnostics must report operational."""
        engine = OmniAIDataSciTeamEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")
        self.assertIn("data_loader", diag["agents"])
        self.assertIn("SchemaProfiler", diag["capabilities"])

    def test_datasci_profiling(self) -> None:
        """AI DS Team profiler must compute stats per column."""
        engine = OmniAIDataSciTeamEngine()
        data = self._make_dataset()
        result = engine.profile_dataset(data)
        self.assertTrue(is_ok(result))

        profiles = unwrap(result)
        self.assertEqual(len(profiles), 3)
        age_prof = next(p for p in profiles if p.name == "age")
        self.assertGreater(age_prof.mean, 0)
        self.assertEqual(age_prof.null_count, 0)

    def test_datasci_cleaning(self) -> None:
        """AI DS Team cleaner agent must fill NaN values."""
        engine = OmniAIDataSciTeamEngine()
        cleaner = engine.orchestrator.get_agent("data_cleaner")
        data = {"val": np.array([1.0, np.nan, 3.0, np.nan, 5.0])}
        result = cleaner.fill_nulls(data, strategy="mean")
        self.assertTrue(is_ok(result))
        cleaned = unwrap(result)["val"]
        self.assertFalse(np.any(np.isnan(cleaned)))
        self.assertAlmostEqual(cleaned[1], 3.0)

    def test_datasci_feature_engineering(self) -> None:
        """AI DS Team feature engineer agent must create interaction features."""
        engine = OmniAIDataSciTeamEngine()
        fe = engine.orchestrator.get_agent("feature_engineer")
        data = {
            "a": np.array([1.0, 2.0, 3.0]),
            "b": np.array([4.0, 5.0, 6.0]),
        }
        result = fe.add_interaction(data, "a", "b", "a_x_b")
        self.assertTrue(is_ok(result))
        self.assertIn("a_x_b", unwrap(result))
        np.testing.assert_array_equal(unwrap(result)["a_x_b"], [4.0, 10.0, 18.0])

    def test_datasci_pipeline_execution(self) -> None:
        """AI DS Team must execute a multi-step pipeline with lineage."""
        engine = OmniAIDataSciTeamEngine()
        data = self._make_dataset()

        steps = [
            DSPipelineStep(
                step_id="clean_step",
                agent_name="data_cleaner",
                action="fill_nulls",
                params={"strategy": "mean"},
                output_key="cleaned_data",
            ),
            DSPipelineStep(
                step_id="fe_step",
                agent_name="feature_engineer",
                action="add_interaction",
                params={"col_a": "age", "col_b": "income", "new_col": "age_income"},
                output_key="engineered_data",
            ),
        ]

        result = engine.run_pipeline(steps, data)
        self.assertTrue(is_ok(result))
        run = unwrap(result)
        self.assertEqual(run.status, "completed")
        self.assertIn("age_income", run.artifacts["engineered_data"])
        self.assertEqual(len(run.steps_executed), 2)

    def test_datasci_viz_histogram(self) -> None:
        """AI DS Team visualizer must compute histogram bins."""
        engine = OmniAIDataSciTeamEngine()
        viz = engine.orchestrator.get_agent("visualizer")
        data = {"values": np.random.randn(100)}
        result = viz.describe_histogram(data, "values", bins=5)
        self.assertTrue(is_ok(result))
        hist = unwrap(result)
        self.assertEqual(len(hist["counts"]), 5)
        self.assertEqual(len(hist["bin_edges"]), 6)


class TestSynapseMLEngine(unittest.TestCase):
    """Integration tests for SynapseML distributed ML engine."""

    def test_synapse_diagnostics(self) -> None:
        """SynapseML diagnostics must report operational."""
        engine = OmniSynapseMLEngine()
        diag = engine.diagnostics()
        self.assertEqual(diag["status"], "operational")
        self.assertIn("LightGBMClassifier", diag["components"])

    def test_synapse_dataframe(self) -> None:
        """SynapseML OmniDataFrame must partition data correctly."""
        engine = OmniSynapseMLEngine()
        data = np.random.rand(100, 5)
        df = engine.create_dataframe(data, partitions=4)
        self.assertEqual(df.count(), 100)
        collected = df.collect()
        self.assertEqual(collected.shape, (100, 5))

    def test_synapse_lightgbm_fit_predict(self) -> None:
        """SynapseML LightGBM must fit and produce predictions."""
        engine = OmniSynapseMLEngine()
        np.random.seed(42)
        X = np.random.rand(50, 3)
        y = (X[:, 0] + X[:, 1] > 1.0).astype(float).reshape(-1, 1)
        data = np.hstack([X, y])

        df = engine.create_dataframe(data, partitions=2)
        lgbm = engine.create_lightgbm_classifier()

        fit_result = lgbm.fit(df)
        self.assertTrue(is_ok(fit_result))

        model = unwrap(fit_result)
        pred_result = model.transform(df)
        self.assertTrue(is_ok(pred_result))

        pred_df = unwrap(pred_result)
        self.assertEqual(pred_df.collect().shape[1], 5)  # 3 features + 1 target + 1 prediction

    def test_synapse_pipeline(self) -> None:
        """SynapseML pipeline must chain estimators and transformers."""
        engine = OmniSynapseMLEngine()
        np.random.seed(42)
        X = np.random.rand(80, 4)
        y = (X[:, 0] > 0.5).astype(float).reshape(-1, 1)
        data = np.hstack([X, y])

        df = engine.create_dataframe(data, partitions=4)
        lgbm = engine.create_lightgbm_classifier()
        pipe = engine.create_pipeline(stages=[lgbm])

        result = pipe.fit(df)
        self.assertTrue(is_ok(result))


if __name__ == "__main__":
    unittest.main()
