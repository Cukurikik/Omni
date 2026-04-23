"""
Semester 8 Batch 26 — Integration Tests
=======================================
Validates all 5 Batch 26 engines:
  1. OmniTextheroEngine
  2. OmniDeepjazzEngine
  3. OmniNeuralcorefEngine
  4. OmniThincEngine
  5. OmniSpiceAIEngine
"""

import unittest
import numpy as np

from omni_texthero_engine import OmniTextheroEngine
from omni_deepjazz_engine import OmniDeepjazzEngine
from omni_neuralcoref_engine import OmniNeuralcorefEngine
from omni_thinc_engine import OmniThincEngine
from omni_spiceai_engine import OmniSpiceAIEngine

# ---------------------------------------------------------------------------
# Monadic Helpers
# ---------------------------------------------------------------------------
def is_ok(result) -> bool:
    return hasattr(result, "value") and not hasattr(result, "error")

def is_err(result) -> bool:
    return hasattr(result, "error") and not hasattr(result, "value")

def unwrap(result):
    return result.value


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------

class TestTextheroEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniTextheroEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_lexical_density(self):
        engine = OmniTextheroEngine()
        calc = engine.get_calculator()
        
        corpus = [
            "This is a theoretical block",
            "This block is highly logical"
        ]
        
        res = calc.calculate_text_density(corpus)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertEqual(out["corpus_docs"], 2)
        self.assertTrue(out["is_dimensionally_stable"])
        self.assertTrue(out["matrix_sparsity_ratio"] > 0)


class TestDeepjazzEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniDeepjazzEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_midi_markov_generation(self):
        engine = OmniDeepjazzEngine()
        sim = engine.get_structural_evaluator()
        
        # Base notes limit
        res = sim.generate_jazz_progression([60, 62, 64], steps=5)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertEqual(out["generated_sequence_length"], 8)
        self.assertTrue(out["is_harmonic_bound"])


class TestNeuralcorefEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniNeuralcorefEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_coreference_resolutions(self):
        engine = OmniNeuralcorefEngine()
        evaluator = engine.get_evaluator()
        
        tokens = ["Elon", "saw", "it", "and", "he", "smiled"]
        pronouns = ["he", "it"]
        
        res = evaluator.resolve_coreferences_numb_array(tokens, pronouns)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_resolved"])
        self.assertTrue(out["clustering_efficiency"] > 0.0)
        self.assertEqual(out["entities_found"], 1) # 'Elon'


class TestThincEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniThincEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_tensor_integrity(self):
        engine = OmniThincEngine()
        validator = engine.get_validator()
        
        shapes = [(10, 50), (50, 20), (20, 5)]
        
        res = validator.validate_tensor_chain_bounds(shapes)
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_statically_pure"])
        self.assertEqual(out["predicted_output_shape"], (10, 5))
        
    def test_tensor_mismatch(self):
        engine = OmniThincEngine()
        validator = engine.get_validator()
        
        # Invalid bounds
        shapes = [(10, 50), (40, 20)]
        res = validator.validate_tensor_chain_bounds(shapes)
        self.assertTrue(is_err(res)) # Fails beautifully


class TestSpiceAIEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniSpiceAIEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_temporal_anomaly(self):
        engine = OmniSpiceAIEngine()
        agg = engine.get_aggregator()
        
        # Execute time stamps
        # Notice the jump between 105 and 500
        timestamps = [100, 102, 105, 500, 502, 505]
        
        res = agg.aggregate_temporal_anomalies(timestamps, tolerance_seconds=20)
        
        self.assertTrue(is_ok(res))
        out = unwrap(res)
        
        self.assertTrue(out["is_indexed"])
        self.assertEqual(out["anomalies_detected"], 1)
        self.assertEqual(out["anomaly_coordinates"][0]["gap_duration"], 395)


if __name__ == "__main__":
    unittest.main()
