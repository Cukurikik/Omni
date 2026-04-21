import unittest
from src.compute.python_core.system.omni_ultrachat_engine import OmniUltraChatEngine
from src.compute.python_core.system.omni_interactive_tools_engine import OmniInteractiveToolsEngine
from src.compute.python_core.system.omni_videopipe_engine import OmniVideoPipeEngine
from src.compute.python_core.system.omni_dl_timeseries_engine import OmniDLTimeSeriesEngine
from src.compute.python_core.system.omni_muzero_engine import OmniMuZeroEngine

class TestOmniUltraChatEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniUltraChatEngine()

    def test_open_session_valid(self):
        res = self.engine.open_session("sess1", "You are a helpful assistant.")
        self.assertEqual(res["status"], "success")

    def test_open_session_duplicate(self):
        self.engine.open_session("sess2", "Sys")
        res = self.engine.open_session("sess2", "Sys")
        self.assertEqual(res["status"], "error")

    def test_inject_turn_unloaded(self):
        res = self.engine.inject_turn("ghost", "Hello")
        self.assertEqual(res["status"], "error")

    def test_inject_turn_empty(self):
        self.engine.open_session("sess3", "Sys")
        res = self.engine.inject_turn("sess3", "")
        self.assertEqual(res["status"], "error")

    def test_inject_turn_valid(self):
        self.engine.open_session("sess4", "Sys")
        res = self.engine.inject_turn("sess4", "Hello there")
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["turn_count"], 1)

    def test_system_status(self):
        res = self.engine.get_system_status()
        self.assertEqual(res["status"], "success")

    def test_instance_creation(self):
        self.assertIsNotNone(self.engine)
    def test_is_not_none(self):
        self.assertIsNotNone(self.engine)
    def test_engine_type(self):
        self.assertIsNotNone(type(self.engine).__name__)

class TestOmniInteractiveToolsEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniInteractiveToolsEngine()

    def test_register_valid(self):
        res = self.engine.register_parameter_space("space1", ["alpha", "beta"])
        self.assertEqual(res["status"], "success")

    def test_register_empty(self):
        res = self.engine.register_parameter_space("space2", [])
        self.assertEqual(res["status"], "error")

    def test_register_duplicate(self):
        self.engine.register_parameter_space("space3", ["alpha"])
        res = self.engine.register_parameter_space("space3", ["beta"])
        self.assertEqual(res["status"], "error")

    def test_trigger_unloaded(self):
        res = self.engine.trigger_visual_update("ghost", {"alpha": 1.0})
        self.assertEqual(res["status"], "error")

    def test_trigger_invalid_param(self):
        self.engine.register_parameter_space("space4", ["alpha"])
        res = self.engine.trigger_visual_update("space4", {"beta": 1.0})
        self.assertEqual(res["status"], "error")

    def test_trigger_valid(self):
        self.engine.register_parameter_space("space5", ["alpha", "beta"])
        res = self.engine.trigger_visual_update("space5", {"alpha": 0.5, "beta": 1.5})
        self.assertEqual(res["status"], "success")
        self.assertAlmostEqual(res["reactive_energy"], 3.0)

    def test_system_status(self):
        res = self.engine.get_system_status()
        self.assertEqual(res["status"], "success")

    def test_instance_creation(self):
        self.assertIsNotNone(self.engine)
    def test_is_not_none(self):
        self.assertIsNotNone(self.engine)
    def test_engine_type(self):
        self.assertIsNotNone(type(self.engine).__name__)

class TestOmniVideoPipeEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniVideoPipeEngine()

    def test_construct_valid(self):
        res = self.engine.construct_pipeline("pipe1", "rtsp")
        self.assertEqual(res["status"], "success")

    def test_construct_invalid_protocol(self):
        res = self.engine.construct_pipeline("pipe2", "fake_proto")
        self.assertEqual(res["status"], "error")

    def test_construct_duplicate(self):
        self.engine.construct_pipeline("pipe3", "hls")
        res = self.engine.construct_pipeline("pipe3", "rtsp")
        self.assertEqual(res["status"], "error")

    def test_extract_unloaded(self):
        res = self.engine.extract_tensors("ghost", 10)
        self.assertEqual(res["status"], "error")

    def test_extract_invalid_frames(self):
        self.engine.construct_pipeline("pipe4", "file")
        res = self.engine.extract_tensors("pipe4", 0)
        self.assertEqual(res["status"], "error")

    def test_extract_valid(self):
        self.engine.construct_pipeline("pipe5", "rtsp")
        res = self.engine.extract_tensors("pipe5", 5)
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["extracted_count"], 5)
        self.assertEqual(len(res["buffers"]), 5)

    def test_system_status(self):
        res = self.engine.get_system_status()
        self.assertEqual(res["status"], "success")

    def test_instance_creation(self):
        self.assertIsNotNone(self.engine)
    def test_is_not_none(self):
        self.assertIsNotNone(self.engine)
    def test_engine_type(self):
        self.assertIsNotNone(type(self.engine).__name__)

class TestOmniDLTimeSeriesEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniDLTimeSeriesEngine()

    def test_compile_valid(self):
        res = self.engine.compile_forecaster("ts1", "LSTM", 10)
        self.assertEqual(res["status"], "success")

    def test_compile_invalid_arch(self):
        res = self.engine.compile_forecaster("ts2", "FakeNet", 10)
        self.assertEqual(res["status"], "error")

    def test_compile_invalid_window(self):
        res = self.engine.compile_forecaster("ts3", "TCN", 0)
        self.assertEqual(res["status"], "error")

    def test_infer_unloaded(self):
        res = self.engine.infer_forecast("ghost", [1.0, 2.0], 5)
        self.assertEqual(res["status"], "error")

    def test_infer_short_sequence(self):
        self.engine.compile_forecaster("ts4", "Transformer", 10)
        res = self.engine.infer_forecast("ts4", [1.0, 2.0], 5)
        self.assertEqual(res["status"], "error")

    def test_infer_invalid_horizon(self):
        self.engine.compile_forecaster("ts5", "LSTM", 5)
        res = self.engine.infer_forecast("ts5", [1.0, 2.0, 3.0, 4.0, 5.0], 0)
        self.assertEqual(res["status"], "error")

    def test_infer_valid(self):
        self.engine.compile_forecaster("ts6", "LSTM", 5)
        res = self.engine.infer_forecast("ts6", [1.0, 2.0, 3.0, 4.0, 5.0], 3)
        self.assertEqual(res["status"], "success")
        self.assertEqual(len(res["forecast"]), 3)

    def test_system_status(self):
        res = self.engine.get_system_status()
        self.assertEqual(res["status"], "success")

    def test_instance_creation(self):
        self.assertIsNotNone(self.engine)
    def test_is_not_none(self):
        self.assertIsNotNone(self.engine)
    def test_engine_type(self):
        self.assertIsNotNone(type(self.engine).__name__)

class TestOmniMuZeroEngine(unittest.TestCase):
    def setUp(self):
        self.engine = OmniMuZeroEngine()

    def test_configure_valid(self):
        res = self.engine.configure_environment("env1", 4, 10)
        self.assertEqual(res["status"], "success")

    def test_configure_duplicate(self):
        self.engine.configure_environment("env2", 4, 10)
        res = self.engine.configure_environment("env2", 2, 5)
        self.assertEqual(res["status"], "error")

    def test_configure_invalid_dims(self):
        res = self.engine.configure_environment("env3", 0, 10)
        self.assertEqual(res["status"], "error")

    def test_execute_unloaded(self):
        res = self.engine.execute_planning("ghost", [1.0])
        self.assertEqual(res["status"], "error")

    def test_execute_mismatched_obs(self):
        self.engine.configure_environment("env4", 4, 10)
        res = self.engine.execute_planning("env4", [1.0, 2.0])
        self.assertEqual(res["status"], "error")

    def test_execute_valid(self):
        self.engine.configure_environment("env5", 4, 3)
        res = self.engine.execute_planning("env5", [1.0, 2.0, 3.0], 50)
        self.assertEqual(res["status"], "success")
        self.assertIn(res["optimal_action"], range(4))
        self.assertEqual(len(res["policy"]), 4)

    def test_system_status(self):
        res = self.engine.get_system_status()
        self.assertEqual(res["status"], "success")

    def test_instance_creation(self):
        self.assertIsNotNone(self.engine)
    def test_is_not_none(self):
        self.assertIsNotNone(self.engine)
    def test_engine_type(self):
        self.assertIsNotNone(type(self.engine).__name__)

if __name__ == '__main__':
    unittest.main()
