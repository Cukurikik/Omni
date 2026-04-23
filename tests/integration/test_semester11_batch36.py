import unittest
from src.compute.python_core.omni_python_development_best_practices_engine import OmniPythonDevelopmentBestPracticesEngine
from src.compute.python_core.omni_college_data_structs_engine import OmniCollegeDataStructsEngine
from src.compute.python_core.omni_practice_git_programming_courses_engine import OmniPracticeGitProgrammingCoursesEngine
from src.compute.python_core.omni_cosdevs_ph_engine import OmniCosdevsPhEngine
from src.compute.python_core.omni_picts_manager_engine import OmniPictsManagerEngine
from src.compute.python_core.omni_software_architecture_design_engine import OmniSoftwareArchitectureDesignEngine
from src.compute.python_core.omni_mtng_engine import OmniMtngEngine
from src.compute.python_core.omni_sadd4ru_engine import OmniSadd4ruEngine
from src.compute.python_core.omni_feri_irawansyah_profile_engine import OmniFeriIrawansyahProfileEngine
from src.compute.python_core.omni_cpp_practice_engine import OmniCppPracticeEngine

class TestSemester11Batch36(unittest.TestCase):
    def setUp(self):
        self.python_best_practices = OmniPythonDevelopmentBestPracticesEngine()
        self.college = OmniCollegeDataStructsEngine(1024)
        self.practice_git = OmniPracticeGitProgrammingCoursesEngine()
        self.cosdevs = OmniCosdevsPhEngine()
        self.picts = OmniPictsManagerEngine()
        self.architecture = OmniSoftwareArchitectureDesignEngine()
        self.mtng = OmniMtngEngine()
        self.sadd4ru = OmniSadd4ruEngine()
        self.feri = OmniFeriIrawansyahProfileEngine()
        self.cpp_practice = OmniCppPracticeEngine()

    # OmniPythonDevelopmentBestPracticesEngine Tests
    def test_python_best_practices_empty(self):
        res = self.python_best_practices.analyze_cyclomatic_complexity([])
        self.assertFalse(res.is_ok())

    def test_python_best_practices_single(self):
        res = self.python_best_practices.analyze_cyclomatic_complexity([10])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 10.0)

    def test_python_best_practices_multiple(self):
        res = self.python_best_practices.analyze_cyclomatic_complexity([10, 20, 30])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 20.0)

    def test_python_best_practices_zeroes(self):
        res = self.python_best_practices.analyze_cyclomatic_complexity([0, 0, 0])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.0)

    def test_python_best_practices_negative(self):
        res = self.python_best_practices.analyze_cyclomatic_complexity([-10, -20])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), -15.0)

    # OmniCollegeDataStructsEngine Tests
    def test_college_structs_offset_aligned(self):
        res = self.college.compute_memory_alignment_offset(16, 8)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 16)

    def test_college_structs_offset_unaligned(self):
        res = self.college.compute_memory_alignment_offset(10, 8)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 16)

    def test_college_structs_offset_unaligned_larger(self):
        res = self.college.compute_memory_alignment_offset(23, 16)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 32)

    def test_college_structs_offset_zero(self):
        res = self.college.compute_memory_alignment_offset(0, 8)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0)

    def test_college_structs_invalid_boundary(self):
        res = self.college.compute_memory_alignment_offset(10, 7)
        self.assertFalse(res.is_ok())

    # OmniPracticeGitProgrammingCoursesEngine Tests
    def test_git_programming_valid_distance(self):
        self.practice_git.commit("A", [])
        self.practice_git.commit("B", ["A"])
        self.practice_git.commit("C", ["B"])
        res = self.practice_git.calculate_merge_distance("A", "C")
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 2)

    def test_git_programming_same_commit(self):
        self.practice_git.commit("A", [])
        res = self.practice_git.calculate_merge_distance("A", "A")
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0)

    def test_git_programming_forked_distance(self):
        self.practice_git.commit("ROOT", [])
        self.practice_git.commit("B1", ["ROOT"])
        self.practice_git.commit("B2", ["ROOT"])
        res = self.practice_git.calculate_merge_distance("B1", "B2")
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 2)

    def test_git_programming_no_common_ancestor(self):
        self.practice_git.commit("Root1", [])
        self.practice_git.commit("Root2", [])
        res = self.practice_git.calculate_merge_distance("Root1", "Root2")
        self.assertFalse(res.is_ok())

    def test_git_programming_invalid_hash(self):
        res = self.practice_git.calculate_merge_distance("NONEXISTENT", "Root2")
        self.assertFalse(res.is_ok())

    # OmniCosdevsPhEngine Tests
    def test_cosdevs_single_node(self):
        self.cosdevs.attach_node("root", "div", None)
        res = self.cosdevs.calculate_component_hierarchy_weight("root")
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 1.0)

    def test_cosdevs_single_child(self):
        self.cosdevs.attach_node("root", "div", None)
        self.cosdevs.attach_node("child", "p", "root")
        res = self.cosdevs.calculate_component_hierarchy_weight("root")
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 1.5)

    def test_cosdevs_multi_child(self):
        self.cosdevs.attach_node("root", "div", None)
        self.cosdevs.attach_node("c1", "p", "root")
        self.cosdevs.attach_node("c2", "p", "root")
        res = self.cosdevs.calculate_component_hierarchy_weight("root")
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 2.0)

    def test_cosdevs_nested_children(self):
        self.cosdevs.attach_node("root", "div", None)
        self.cosdevs.attach_node("c1", "div", "root")
        self.cosdevs.attach_node("gc1", "span", "c1")
        res = self.cosdevs.calculate_component_hierarchy_weight("root")
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 1.75)

    def test_cosdevs_missing_root(self):
        res = self.cosdevs.calculate_component_hierarchy_weight("404")
        self.assertFalse(res.is_ok())

    # OmniPictsManagerEngine Tests
    def test_picts_manager_valid_compression(self):
        res = self.picts.extract_compression_ratio(100, 50)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 2.0)

    def test_picts_manager_zero_compressed(self):
        res = self.picts.extract_compression_ratio(100, 0)
        self.assertFalse(res.is_ok())

    def test_picts_manager_zero_uncompressed(self):
        res = self.picts.extract_compression_ratio(0, 50)
        self.assertFalse(res.is_ok())

    def test_picts_manager_negative_values(self):
        res = self.picts.extract_compression_ratio(-10, -5)
        self.assertFalse(res.is_ok())

    def test_picts_manager_no_compression(self):
        res = self.picts.extract_compression_ratio(100, 100)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 1.0)

    # OmniSoftwareArchitectureDesignEngine Tests
    def test_software_arch_no_components(self):
        res = self.architecture.measure_coupling_factor()
        self.assertFalse(res.is_ok())

    def test_software_arch_one_component(self):
        self.architecture.register_component("A", 1)
        res = self.architecture.measure_coupling_factor()
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.0)

    def test_software_arch_two_components_no_deps(self):
        self.architecture.register_component("A", 1)
        self.architecture.register_component("B", 1)
        res = self.architecture.measure_coupling_factor()
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.0)

    def test_software_arch_two_components_one_dep(self):
        self.architecture.register_component("A", 1)
        self.architecture.register_component("B", 1)
        self.architecture.add_dependency("A", "B")
        res = self.architecture.measure_coupling_factor()
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.5)

    def test_software_arch_two_components_full_coupling(self):
        self.architecture.register_component("A", 1)
        self.architecture.register_component("B", 1)
        self.architecture.add_dependency("A", "B")
        self.architecture.add_dependency("B", "A")
        res = self.architecture.measure_coupling_factor()
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 1.0)

    # OmniMtngEngine Tests
    def test_mtng_no_slides(self):
        res = self.mtng.optimize_slide_allocation(10)
        self.assertFalse(res.is_ok())

    def test_mtng_negative_tokens(self):
        self.mtng.compile_slide("S1", "abcde")
        res = self.mtng.optimize_slide_allocation(-5)
        self.assertFalse(res.is_ok())

    def test_mtng_no_overflow(self):
        self.mtng.compile_slide("S1", "abcde")
        res = self.mtng.optimize_slide_allocation(10)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0)

    def test_mtng_with_overflow(self):
        self.mtng.compile_slide("S1", "abcdefghij") # 10 tokens
        self.mtng.compile_slide("S2", "abcde")      # 5 tokens
        res = self.mtng.optimize_slide_allocation(8)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 2)

    def test_mtng_multiple_overflows(self):
        self.mtng.compile_slide("S1", "abcdefghij") # 10 tokens
        self.mtng.compile_slide("S2", "abcdefgh")   # 8 tokens
        res = self.mtng.optimize_slide_allocation(5)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 8)

    # OmniSadd4ruEngine Tests
    def test_sadd4ru_no_requirements(self):
        res = self.sadd4ru.validate_architectural_drift(10)
        self.assertFalse(res.is_ok())

    def test_sadd4ru_zero_expected(self):
        self.sadd4ru.register_requirement("R1", 5)
        res = self.sadd4ru.validate_architectural_drift(0)
        self.assertFalse(res.is_ok())

    def test_sadd4ru_no_drift(self):
        self.sadd4ru.register_requirement("R1", 5)
        self.sadd4ru.register_requirement("R2", 5)
        res = self.sadd4ru.validate_architectural_drift(10)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.0)

    def test_sadd4ru_positive_drift(self):
        self.sadd4ru.register_requirement("R1", 8)
        res = self.sadd4ru.validate_architectural_drift(5)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.6)

    def test_sadd4ru_negative_drift(self):
        self.sadd4ru.register_requirement("R1", 5)
        res = self.sadd4ru.validate_architectural_drift(10)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.5)

    # OmniFeriIrawansyahProfileEngine Tests
    def test_feri_empty_viewports(self):
        res = self.feri.calculate_layout_shifts([])
        self.assertFalse(res.is_ok())

    def test_feri_single_viewport(self):
        res = self.feri.calculate_layout_shifts([1.0])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.0)

    def test_feri_two_viewports(self):
        res = self.feri.calculate_layout_shifts([1.0, 2.5])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 1.5)

    def test_feri_oscillating_viewports(self):
        res = self.feri.calculate_layout_shifts([1.0, 0.5, 1.0])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 1.0)

    def test_feri_static_viewports(self):
        res = self.feri.calculate_layout_shifts([1.0, 1.0, 1.0])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.0)

    # OmniCppPracticeEngine Tests
    def test_cpp_practice_empty_allocations(self):
        res = self.cpp_practice.calculate_pointer_entropy()
        self.assertFalse(res.is_ok())

    def test_cpp_practice_single_allocation(self):
        self.cpp_practice.malloc("ptr1", 100)
        res = self.cpp_practice.calculate_pointer_entropy()
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.0)

    def test_cpp_practice_duplicate_allocation(self):
        self.cpp_practice.malloc("ptr1", 100)
        self.cpp_practice.malloc("ptr2", 100)
        res = self.cpp_practice.calculate_pointer_entropy()
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 1.0)

    def test_cpp_practice_three_allocations(self):
        self.cpp_practice.malloc("ptr1", 100)
        self.cpp_practice.malloc("ptr2", 100)
        self.cpp_practice.malloc("ptr3", 200)
        res = self.cpp_practice.calculate_pointer_entropy()
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 1.5)

    def test_cpp_practice_freed_allocations(self):
        self.cpp_practice.malloc("ptr1", 100)
        self.cpp_practice.malloc("ptr2", 100)
        self.cpp_practice.free("ptr2")
        res = self.cpp_practice.calculate_pointer_entropy()
        self.assertTrue(res.is_ok())
        self.assertEqual(res.unwrap(), 0.0)

if __name__ == '__main__':
    unittest.main()
