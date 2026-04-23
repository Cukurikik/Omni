"""
Semester 8 Batch 15 — Integration Tests
=======================================
Validates all 5 Batch 15 engines:
  1. OmniDJLEngine
  2. OmniSpandanDLEngine
  3. OmniOpenMLSysEngine
  4. OmniKilnEngine
  5. OmniMLFinLabEngine
"""

import unittest
import numpy as np

from omni_djl_engine import OmniDJLEngine
from omni_spandan_dl_engine import OmniSpandanDLEngine, Configuration
from omni_openmlsys_engine import OmniOpenMLSysEngine, ComputatonTask
from omni_kiln_engine import OmniKilnEngine, PromptRecord
from omni_mlfinlab_engine import OmniMLFinLabEngine

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

class TestDJLEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniDJLEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_djl_workflow(self):
        engine = OmniDJLEngine()
        model_res = engine.load_model("prod_resnet")
        self.assertTrue(is_ok(model_res))
        
        predictor = engine.create_predictor(unwrap(model_res))
        
        # input data
        raw_input = [1.0, 2.0]
        pred_res = predictor.predict(raw_input)
        self.assertTrue(is_ok(pred_res))
        
        output = unwrap(pred_res)
        self.assertEqual(len(output), 2)
        # Verify manager closed out resources automatically
        self.assertTrue(predictor.manager.is_closed)


class TestSpandanDLEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniSpandanDLEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_modular_training(self):
        engine = OmniSpandanDLEngine()
        config = Configuration(epochs=3, batch_size=2)
        trainer = engine.create_trainer(config)
        
        x = np.array([[1.0], [2.0], [3.0], [4.0]])
        y = np.array([[0.5], [1.0], [1.5], [2.0]])
        
        data_loader = engine.create_loader(x, y, 2)
        
        res = trainer.train(data_loader, val_loader=data_loader)
        self.assertTrue(is_ok(res))
        
        history = unwrap(res)
        self.assertEqual(len(history), 3) # 3 epochs
        self.assertIn("train_loss", history[0])
        self.assertIn("val_loss", history[0])


class TestOpenMLSysEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniOpenMLSysEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_dag_scheduler(self):
        engine = OmniOpenMLSysEngine()
        dag = engine.create_dag()
        
        t1 = ComputatonTask.new("LoadData")
        t2 = ComputatonTask.new("MatMul", deps=[t1.id])
        t3 = ComputatonTask.new("Loss", deps=[t2.id])
        
        dag.add_task(t1)
        dag.add_task(t3)
        dag.add_task(t2)
        
        sched = engine.create_scheduler(workers=2)
        plan_res = sched.schedule(dag)
        self.assertTrue(is_ok(plan_res))
        
        plan = unwrap(plan_res)
        self.assertEqual(len(plan), 3)
        self.assertIn(t1.id, plan)


class TestKilnEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniKilnEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_active_learning(self):
        engine = OmniKilnEngine()
        pipeline = engine.get_pipeline(threshold=0.5)
        
        batch = [
            PromptRecord("How to code?", "I don't know."), # low score 0.0 - 0.5 < 0
            PromptRecord("Why sky blue?", "Because of Rayleigh scattering."), # has 'because' = 0.3 + length > 20 (0.2) = 0.5
            PromptRecord("Write a book.", "It is a long text." * 10) # 0.5 (length > 100)
        ]
        
        res = pipeline.process_batch(batch)
        self.assertTrue(is_ok(res))
        metrics = unwrap(res)
        
        self.assertEqual(metrics["processed"], 3)
        self.assertEqual(metrics["accepted"], 2)


class TestMLFinLabEngine(unittest.TestCase):
    def test_diagnostics(self):
        engine = OmniMLFinLabEngine()
        self.assertEqual(engine.diagnostics()["status"], "operational")

    def test_dollar_bars_and_barrier(self):
        engine = OmniMLFinLabEngine()
        
        # [Time, Price, Volume]
        ticks = np.array([
            [1.0, 100.0, 10],   # dollar = 1000
            [2.0, 101.0, 10],   # dollar = 1010
            [3.0, 102.0, 5],    # dollar = 510 -> aggregate > 2000
            [4.0, 99.0, 20],    # dollar = 1980
            [5.0, 95.0, 5],     # dollar = 475 -> aggr > 2000
        ])
        
        sampler = engine.get_sampler()
        res_bars = sampler.dollar_bars(ticks, threshold=2000.0)
        self.assertTrue(is_ok(res_bars))
        
        bars = unwrap(res_bars)
        self.assertEqual(len(bars), 2)
        
        labeler = engine.get_labeler()
        closing_prices = np.array([100.0, 101.0, 102.0, 99.0, 95.0, 105.0])
        # Look forward 2 steps, PT 4%, SL 4%
        lbl_res = labeler.triple_barrier(closing_prices, upper_pt=0.04, lower_sl=0.04, t_max=2)
        self.assertTrue(is_ok(lbl_res))
        
        labels = unwrap(lbl_res)
        self.assertEqual(len(labels), 6)
        # at index 0 (100), hitting 104 or 96 in next 2 steps (101, 102) -> hits neither, returns 0
        self.assertEqual(labels[0], 0)
        # at index 3 (99), hitting 95.04 or 102.96 in next 2 steps (95, 105) -> hits 95 (down) first -> -1
        self.assertEqual(labels[3], -1)


if __name__ == "__main__":
    unittest.main()
