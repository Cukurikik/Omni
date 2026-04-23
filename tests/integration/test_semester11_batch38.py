import unittest
from src.compute.python_core.omni_hacker_or_id_system_engine import OmniHackerOrIdSystemEngine
from src.compute.python_core.omni_scaling_couscous_engine import OmniScalingCouscousEngine
from src.compute.python_core.omni_iron_oxidation_simulator_engine import OmniIronOxidationSimulatorEngine
from src.compute.python_core.omni_pcp_software_engine import OmniPcpSoftwareEngine
from src.compute.python_core.omni_candymanager_engine import OmniCandymanagerEngine
from src.compute.python_core.omni_bytecore_engine import OmniBytecoreEngine
from src.compute.python_core.omni_superhero_squad_engine import OmniSuperheroSquadEngine
from src.compute.python_core.omni_cyberc00z_legacy_engine import OmniCyberc00zLegacyEngine
from src.compute.python_core.omni_marv0_blog_engine import OmniMarv0BlogEngine
from src.compute.python_core.omni_ismael_k_vhdl_engine import OmniIsmaelKVHDLEngine

class TestSemester11Batch38(unittest.TestCase):
    def setUp(self):
        self.system = OmniHackerOrIdSystemEngine()
        self.scaling = OmniScalingCouscousEngine()
        self.iron = OmniIronOxidationSimulatorEngine()
        self.pcp = OmniPcpSoftwareEngine()
        self.candy = OmniCandymanagerEngine()
        self.bytecore = OmniBytecoreEngine()
        self.superhero = OmniSuperheroSquadEngine()
        self.legacy = OmniCyberc00zLegacyEngine()
        self.marv = OmniMarv0BlogEngine()
        self.vhdl = OmniIsmaelKVHDLEngine()

    # OmniHackerOrIdSystemEngine Tests
    def test_system_valid_wait(self):
        res = self.system.calculate_cpu_wait_times(10.0, 5)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 12.5)

    def test_system_zero_interrupts(self):
        res = self.system.calculate_cpu_wait_times(10.0, 0)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 10.0)

    def test_system_negative_base(self):
        res = self.system.calculate_cpu_wait_times(-10.0, 5)
        self.assertFalse(res.is_ok())

    def test_system_negative_interrupts(self):
        res = self.system.calculate_cpu_wait_times(10.0, -5)
        self.assertFalse(res.is_ok())

    def test_system_large_interrupts(self):
        res = self.system.calculate_cpu_wait_times(10.0, 100)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 60.0)

    # OmniScalingCouscousEngine Tests
    def test_scaling_valid_factor(self):
        res = self.scaling.compute_scale_factor(1920, 3840)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 2.0)

    def test_scaling_downscale(self):
        res = self.scaling.compute_scale_factor(3840, 1920)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.5)

    def test_scaling_zero_base(self):
        res = self.scaling.compute_scale_factor(0, 3840)
        self.assertFalse(res.is_ok())

    def test_scaling_negative_target(self):
        res = self.scaling.compute_scale_factor(1920, -100)
        self.assertFalse(res.is_ok())

    def test_scaling_equal_res(self):
        res = self.scaling.compute_scale_factor(1080, 1080)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 1.0)

    # OmniIronOxidationSimulatorEngine Tests
    def test_iron_valid_rate(self):
        res = self.iron.simulate_oxidation_rate(100.0, 0.5, 2.0)
        self.assertTrue(res.is_ok())
        self.assertAlmostEqual(res.unwrap(), 60.5)

    def test_iron_negative_mass(self):
        res = self.iron.simulate_oxidation_rate(-100.0, 0.5, 2.0)
        self.assertFalse(res.is_ok())

    def test_iron_invalid_oxygen(self):
        res = self.iron.simulate_oxidation_rate(100.0, 1.5, 2.0)
        self.assertFalse(res.is_ok())

    def test_iron_negative_time(self):
        res = self.iron.simulate_oxidation_rate(100.0, 0.5, -2.0)
        self.assertFalse(res.is_ok())

    def test_iron_zero_oxygen(self):
        res = self.iron.simulate_oxidation_rate(100.0, 0.0, 2.0)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.0)

    # OmniPcpSoftwareEngine Tests
    def test_pcp_valid_error(self):
        res = self.pcp.calculate_calibration_error(10.5, 10.0)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 5.0)

    def test_pcp_zero_true_distance(self):
        res = self.pcp.calculate_calibration_error(10.5, 0.0)
        self.assertFalse(res.is_ok())

    def test_pcp_negative_measured(self):
        res = self.pcp.calculate_calibration_error(-10.5, 10.0)
        self.assertFalse(res.is_ok())

    def test_pcp_negative_true(self):
        res = self.pcp.calculate_calibration_error(10.5, -10.0)
        self.assertFalse(res.is_ok())

    def test_pcp_exact_calibration(self):
        res = self.pcp.calculate_calibration_error(15.0, 15.0)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.0)

    # OmniCandymanagerEngine Tests
    def test_candy_sufficient_stock(self):
        res = self.candy.optimize_stock_levels(100, 10.0, 5)
        self.assertTrue(res.is_ok())
        self.assertTrue(res.unwrap())

    def test_candy_insufficient_stock(self):
        res = self.candy.optimize_stock_levels(40, 10.0, 5)
        self.assertTrue(res.is_ok())
        self.assertFalse(res.unwrap())

    def test_candy_negative_stock(self):
        res = self.candy.optimize_stock_levels(-10, 10.0, 5)
        self.assertFalse(res.is_ok())

    def test_candy_negative_consumption(self):
        res = self.candy.optimize_stock_levels(100, -10.0, 5)
        self.assertFalse(res.is_ok())

    def test_candy_exact_stock(self):
        res = self.candy.optimize_stock_levels(50, 10.0, 5)
        self.assertTrue(res.is_ok())
        self.assertTrue(res.unwrap())

    # OmniBytecoreEngine Tests
    def test_bytecore_valid_cycles(self):
        res = self.bytecore.compute_instruction_cycles(4, 2)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 6)

    def test_bytecore_zero_base(self):
        res = self.bytecore.compute_instruction_cycles(0, 2)
        self.assertFalse(res.is_ok())

    def test_bytecore_negative_wait(self):
        res = self.bytecore.compute_instruction_cycles(4, -1)
        self.assertFalse(res.is_ok())

    def test_bytecore_zero_wait(self):
        res = self.bytecore.compute_instruction_cycles(4, 0)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 4)

    def test_bytecore_large_cycles(self):
        res = self.bytecore.compute_instruction_cycles(100, 50)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 150)

    # OmniSuperheroSquadEngine Tests
    def test_superhero_valid_power(self):
        res = self.superhero.calculate_hero_power_level(100, 1.5, 0.2)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 120.0)

    def test_superhero_negative_strength(self):
        res = self.superhero.calculate_hero_power_level(-100, 1.5, 0.2)
        self.assertFalse(res.is_ok())

    def test_superhero_negative_multiplier(self):
        res = self.superhero.calculate_hero_power_level(100, -1.5, 0.2)
        self.assertFalse(res.is_ok())

    def test_superhero_invalid_fatigue(self):
        res = self.superhero.calculate_hero_power_level(100, 1.5, 1.2)
        self.assertFalse(res.is_ok())

    def test_superhero_max_fatigue(self):
        res = self.superhero.calculate_hero_power_level(100, 1.5, 1.0)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.0)

    # OmniCyberc00zLegacyEngine Tests
    def test_legacy_valid_score(self):
        res = self.legacy.compute_legacy_debt_score(1000, 10)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 125.0)

    def test_legacy_negative_lines(self):
        res = self.legacy.compute_legacy_debt_score(-1000, 10)
        self.assertFalse(res.is_ok())

    def test_legacy_negative_warnings(self):
        res = self.legacy.compute_legacy_debt_score(1000, -10)
        self.assertFalse(res.is_ok())

    def test_legacy_zero_debt(self):
        res = self.legacy.compute_legacy_debt_score(0, 0)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.0)

    def test_legacy_high_warnings(self):
        res = self.legacy.compute_legacy_debt_score(100, 100)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 260.0)

    # OmniMarv0BlogEngine Tests
    def test_marv_valid_time(self):
        res = self.marv.estimate_read_time(500, 4)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 4.0)

    def test_marv_negative_words(self):
        res = self.marv.estimate_read_time(-500, 4)
        self.assertFalse(res.is_ok())

    def test_marv_negative_images(self):
        res = self.marv.estimate_read_time(500, -4)
        self.assertFalse(res.is_ok())

    def test_marv_zero_both(self):
        res = self.marv.estimate_read_time(0, 0)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.0)

    def test_marv_only_images(self):
        res = self.marv.estimate_read_time(0, 10)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 5.0)

    # OmniIsmaelKVHDLEngine Tests
    def test_vhdl_valid_delay(self):
        res = self.vhdl.calculate_gate_delay(1.5, 3)
        self.assertTrue(res.is_ok())
        self.assertAlmostEqual(res.unwrap(), 2.1)

    def test_vhdl_negative_base(self):
        res = self.vhdl.calculate_gate_delay(-1.5, 3)
        self.assertFalse(res.is_ok())

    def test_vhdl_negative_fanout(self):
        res = self.vhdl.calculate_gate_delay(1.5, -3)
        self.assertFalse(res.is_ok())

    def test_vhdl_zero_fanout(self):
        res = self.vhdl.calculate_gate_delay(1.5, 0)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 1.5)

    def test_vhdl_high_fanout(self):
        res = self.vhdl.calculate_gate_delay(1.0, 20)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 5.0)

if __name__ == '__main__':
    unittest.main()
