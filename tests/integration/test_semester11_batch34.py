import pytest
from src.compute.python_core.omni_python_development_best_practices_engine import OmniPythonDevelopmentBestPracticesEngine
from src.compute.python_core.omni_college_data_structure_engine import OmniCollegeDataStructureEngine
from src.compute.python_core.omni_practice_git_programming_courses_engine import OmniPracticeGitProgrammingCoursesEngine
from src.compute.python_core.omni_cosdevs_ph_engine import OmniCosdevsPhEngine
from src.compute.python_core.omni_picts_manager_engine import OmniPictsManagerEngine
from src.compute.python_core.omni_software_architecture_design_engine import OmniSoftwareArchitectureDesignEngine
from src.compute.python_core.omni_mtng_engine import OmniMtngEngine
from src.compute.python_core.omni_sadd4ru_engine import OmniSadd4ruEngine
from src.compute.python_core.omni_feri_irawansyah_profile_engine import OmniFeriIrawansyahProfileEngine
from src.compute.python_core.omni_cpp_practice_engine import OmniCppPracticeEngine

class TestSemester11Batch34:
    # --- OmniPythonDevelopmentBestPracticesEngine (5) ---
    def test_py_best_practice_register(self):
        engine = OmniPythonDevelopmentBestPracticesEngine()
        assert engine.register_rule("PEP8", 10).is_ok()
        assert not engine.register_rule("PEP8", 5).is_ok()

    def test_py_best_practice_invalid_rule(self):
        engine = OmniPythonDevelopmentBestPracticesEngine()
        assert not engine.register_rule("", 10).is_ok()
        assert not engine.register_rule("RULE", 0).is_ok()

    def test_py_best_practice_eval(self):
        engine = OmniPythonDevelopmentBestPracticesEngine()
        engine.register_rule("PEP8", 10)
        engine.register_rule("TYPE_HINTS", 20)
        res = engine.evaluate_code({"PEP8": True, "TYPE_HINTS": False}).unwrap()
        assert res == 0  # 10 - (20 * 0.5) = 10 - 10 = 0

    def test_py_best_practice_eval_all_pass(self):
        engine = OmniPythonDevelopmentBestPracticesEngine()
        engine.register_rule("A", 10)
        engine.register_rule("B", 10)
        assert engine.evaluate_code({"A": True, "B": True}).unwrap() == 20

    def test_py_best_practice_no_rules_eval(self):
        engine = OmniPythonDevelopmentBestPracticesEngine()
        assert not engine.evaluate_code({"A": True}).is_ok()

    # --- OmniCollegeDataStructureEngine (5) ---
    def test_data_struct_insert(self):
        engine = OmniCollegeDataStructureEngine()
        assert engine.insert_node(10).is_ok()
        assert engine.insert_node(5).is_ok()
        assert engine.insert_node(15).is_ok()

    def test_data_struct_insert_invalid(self):
        engine = OmniCollegeDataStructureEngine()
        assert not engine.insert_node(-1).is_ok()

    def test_data_struct_insert_duplicate(self):
        engine = OmniCollegeDataStructureEngine()
        engine.insert_node(10)
        assert not engine.insert_node(10).is_ok()

    def test_data_struct_max_depth(self):
        engine = OmniCollegeDataStructureEngine()
        engine.insert_node(10)
        engine.insert_node(5)
        engine.insert_node(15)
        engine.insert_node(20)
        assert engine.compute_max_depth().unwrap() == 3

    def test_data_struct_depth_empty(self):
        engine = OmniCollegeDataStructureEngine()
        assert not engine.compute_max_depth().is_ok()

    # --- OmniPracticeGitProgrammingCoursesEngine (5) ---
    def test_git_commit(self):
        engine = OmniPracticeGitProgrammingCoursesEngine()
        assert engine.commit("A", []).is_ok()
        assert engine.commit("B", ["A"]).is_ok()

    def test_git_commit_invalid(self):
        engine = OmniPracticeGitProgrammingCoursesEngine()
        assert not engine.commit("B", ["A"]).is_ok() # A missing

    def test_git_commit_dup(self):
        engine = OmniPracticeGitProgrammingCoursesEngine()
        engine.commit("A", [])
        assert not engine.commit("A", []).is_ok()

    def test_git_ancestry(self):
        engine = OmniPracticeGitProgrammingCoursesEngine()
        engine.commit("A", [])
        engine.commit("B", ["A"])
        engine.commit("C", ["A"])
        engine.commit("D", ["B", "C"])
        ancestors = engine.resolve_ancestry("D").unwrap()
        assert len(ancestors) == 4
        assert "A" in ancestors

    def test_git_ancestry_not_found(self):
        engine = OmniPracticeGitProgrammingCoursesEngine()
        assert not engine.resolve_ancestry("Z").is_ok()

    # --- OmniCosdevsPhEngine (5) ---
    def test_cosdevs_attach(self):
        engine = OmniCosdevsPhEngine()
        assert engine.attach_node("root", "div").is_ok()
        assert engine.attach_node("child", "p", "root").is_ok()

    def test_cosdevs_duplicate(self):
        engine = OmniCosdevsPhEngine()
        engine.attach_node("root", "div")
        assert not engine.attach_node("root", "div").is_ok()

    def test_cosdevs_bad_parent(self):
        engine = OmniCosdevsPhEngine()
        assert not engine.attach_node("c1", "p", "ghost").is_ok()

    def test_cosdevs_depth_empty(self):
        engine = OmniCosdevsPhEngine()
        assert not engine.compute_dom_depth().is_ok()

    def test_cosdevs_depth_compute(self):
        engine = OmniCosdevsPhEngine()
        engine.attach_node("r", "div")
        engine.attach_node("c1", "div", "r")
        engine.attach_node("c2", "div", "c1")
        assert engine.compute_dom_depth().unwrap() == 3

    # --- OmniPictsManagerEngine (5) ---
    def test_picts_index(self):
        engine = OmniPictsManagerEngine()
        assert engine.index_picture("p1", 1920, 1080).is_ok()

    def test_picts_invalid_dim(self):
        engine = OmniPictsManagerEngine()
        assert not engine.index_picture("p2", 0, 1080).is_ok()

    def test_picts_duplicate(self):
        engine = OmniPictsManagerEngine()
        engine.index_picture("p1", 1920, 1080)
        assert not engine.index_picture("p1", 800, 600).is_ok()

    def test_picts_filter(self):
        engine = OmniPictsManagerEngine()
        engine.index_picture("p1", 100, 100) # 1.0
        engine.index_picture("p2", 200, 100) # 2.0
        engine.index_picture("p3", 300, 100) # 3.0
        
        assert engine.filter_by_aspect_ratio(1.5, 2.5).unwrap() == 1

    def test_picts_filter_invalid(self):
        engine = OmniPictsManagerEngine()
        assert not engine.filter_by_aspect_ratio(2.0, 1.0).is_ok()

    # --- OmniSoftwareArchitectureDesignEngine (5) ---
    def test_arch_register(self):
        engine = OmniSoftwareArchitectureDesignEngine()
        assert engine.register_component("UI", 3).is_ok()
        assert not engine.register_component("UI", 2).is_ok()

    def test_arch_invalid_layer(self):
        engine = OmniSoftwareArchitectureDesignEngine()
        assert not engine.register_component("DB", -1).is_ok()

    def test_arch_add_dep(self):
        engine = OmniSoftwareArchitectureDesignEngine()
        engine.register_component("UI", 3)
        engine.register_component("Core", 2)
        assert engine.add_dependency("UI", "Core").is_ok()
        
    def test_arch_add_missing_dep(self):
        engine = OmniSoftwareArchitectureDesignEngine()
        engine.register_component("UI", 3)
        assert not engine.add_dependency("UI", "Core").is_ok()

    def test_arch_validation(self):
        engine = OmniSoftwareArchitectureDesignEngine()
        engine.register_component("UI", 3)
        engine.register_component("Core", 2)
        engine.register_component("DB", 1)
        engine.add_dependency("UI", "Core")
        engine.add_dependency("Core", "DB")
        assert engine.validate_layer_isolation().is_ok()
        
        # introduce violation
        engine.add_dependency("DB", "UI")
        assert not engine.validate_layer_isolation().is_ok()

    # --- OmniMtngEngine (5) ---
    def test_mtng_compile(self):
        engine = OmniMtngEngine()
        assert engine.compile_slide("s1", "abc").is_ok()
        assert not engine.compile_slide("s1", "def").is_ok()

    def test_mtng_compile_empty(self):
        engine = OmniMtngEngine()
        assert not engine.compile_slide("", "a").is_ok()

    def test_mtng_build_empty(self):
        engine = OmniMtngEngine()
        assert not engine.build_presentation().is_ok()

    def test_mtng_build(self):
        engine = OmniMtngEngine()
        engine.compile_slide("s1", "hello")
        engine.compile_slide("s2", "world")
        res = engine.build_presentation().unwrap()
        assert res == 110 # 5+50 + 5+50

    def test_mtng_diagnostics(self):
        engine = OmniMtngEngine()
        engine.compile_slide("s1", "hello")
        assert engine.diagnostics()["slide_count"] == 1

    # --- OmniSadd4ruEngine (5) ---
    def test_sadd_reg(self):
        engine = OmniSadd4ruEngine()
        assert engine.register_requirement("R1", 5).is_ok()

    def test_sadd_reg_invalid(self):
        engine = OmniSadd4ruEngine()
        assert not engine.register_requirement("R1", 11).is_ok()
        assert not engine.register_requirement("R1", 0).is_ok()

    def test_sadd_reg_dup(self):
        engine = OmniSadd4ruEngine()
        engine.register_requirement("R1", 5)
        assert not engine.register_requirement("R1", 5).is_ok()

    def test_sadd_estimate(self):
        engine = OmniSadd4ruEngine()
        engine.register_requirement("R1", 2)
        engine.register_requirement("R2", 4)
        engine.register_requirement("R3", 6)
        assert engine.estimate_architectural_effort().unwrap() == 96 # 12 * 8

    def test_sadd_estimate_empty(self):
        engine = OmniSadd4ruEngine()
        assert not engine.estimate_architectural_effort().is_ok()

    # --- OmniFeriIrawansyahProfileEngine (5) ---
    def test_feri_add(self):
        engine = OmniFeriIrawansyahProfileEngine()
        assert engine.add_stylesheet_rule(".class", 10).is_ok()
        assert not engine.add_stylesheet_rule("", 10).is_ok()

    def test_feri_negative_spec(self):
        engine = OmniFeriIrawansyahProfileEngine()
        assert not engine.add_stylesheet_rule(".c", -1).is_ok()

    def test_feri_match(self):
        engine = OmniFeriIrawansyahProfileEngine()
        engine.add_stylesheet_rule("div", 1)
        engine.add_stylesheet_rule(".big", 10)
        engine.add_stylesheet_rule("#hero", 100)
        
        # pass class and tag
        res = engine.match_element(["div", ".big"]).unwrap()
        assert res == 10

    def test_feri_no_match(self):
        engine = OmniFeriIrawansyahProfileEngine()
        engine.add_stylesheet_rule("div", 1)
        assert not engine.match_element(["span"]).is_ok()

    def test_feri_empty_match(self):
        engine = OmniFeriIrawansyahProfileEngine()
        assert not engine.match_element([]).is_ok()

    # --- OmniCppPracticeEngine (5) ---
    def test_cpp_malloc(self):
        engine = OmniCppPracticeEngine()
        assert engine.malloc("0x1", 100).is_ok()
        assert not engine.malloc("0x1", 50).is_ok()

    def test_cpp_malloc_invalid(self):
        engine = OmniCppPracticeEngine()
        assert not engine.malloc("0x2", 0).is_ok()

    def test_cpp_free(self):
        engine = OmniCppPracticeEngine()
        engine.malloc("0x1", 100)
        assert engine.free("0x1").is_ok()
        assert not engine.free("0x1").is_ok() # Double free

    def test_cpp_free_invalid(self):
        engine = OmniCppPracticeEngine()
        assert not engine.free("0x999").is_ok()

    def test_cpp_leak(self):
        engine = OmniCppPracticeEngine()
        engine.malloc("0x1", 100)
        engine.malloc("0x2", 200)
        engine.free("0x1")
        assert engine.compute_memory_leak().unwrap() == 200
