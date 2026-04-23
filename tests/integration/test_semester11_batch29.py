import unittest
from src.compute.python_core.omni_dup_clean_hash_engine import OmniDupCleanHashEngine
from src.compute.python_core.omni_parallel_merge_sort_engine import OmniParallelMergeSortEngine
from src.compute.python_core.omni_biometric_auth_logic_engine import OmniBiometricAuthLogicEngine
from src.compute.python_core.omni_course_allocator_engine import OmniCourseAllocatorEngine
from src.compute.python_core.omni_fitness_metrics_engine import OmniFitnessMetricsEngine
from src.compute.python_core.omni_medication_schedule_engine import OmniMedicationScheduleEngine
from src.compute.python_core.omni_static_site_generator_engine import OmniStaticSiteGeneratorEngine
from src.compute.python_core.omni_job_matcher_engine import OmniJobMatcherEngine
from src.compute.python_core.omni_custom_stack_calculator_engine import OmniCustomStackCalculatorEngine
from src.compute.python_core.omni_project_scaffold_engine import OmniProjectScaffoldEngine


class TestSemester11Batch29(unittest.TestCase):

    def test_instantiation_and_diagnostics(self):
        engines = [
            OmniDupCleanHashEngine(),
            OmniParallelMergeSortEngine(),
            OmniBiometricAuthLogicEngine(),
            OmniCourseAllocatorEngine(),
            OmniFitnessMetricsEngine(),
            OmniMedicationScheduleEngine(),
            OmniStaticSiteGeneratorEngine(),
            OmniJobMatcherEngine(),
            OmniCustomStackCalculatorEngine(),
            OmniProjectScaffoldEngine()
        ]
        count = 0
        for e in engines:
            diag = e.diagnostics()
            self.assertEqual(diag.get("status"), "operational")
            count += 1
        self.assertEqual(count, 10)

    # 1. OmniDupCleanHashEngine
    def test_dup_clean_success(self):
        engine = OmniDupCleanHashEngine()
        data = [b"hello", b"world", b"hello", b"foo"]
        res = engine.detect_duplicates(data)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["total_chunks"], 4)
        self.assertEqual(res.value["unique_chunks"], 3)
        self.assertEqual(len(res.value["duplicate_groups"]), 1)
        self.assertEqual(res.value["duplicate_groups"][0]["indices"], [0, 2])

    def test_dup_clean_empty(self):
        engine = OmniDupCleanHashEngine()
        res = engine.detect_duplicates([])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["total_chunks"], 0)
        self.assertEqual(res.value["unique_chunks"], 0)

    def test_dup_clean_no_dups(self):
        engine = OmniDupCleanHashEngine()
        data = [b"a", b"b", b"c"]
        res = engine.detect_duplicates(data)
        self.assertTrue(res.is_ok())
        self.assertEqual(len(res.value["duplicate_groups"]), 0)

    def test_dup_clean_all_dups(self):
        engine = OmniDupCleanHashEngine()
        data = [b"x", b"x", b"x"]
        res = engine.detect_duplicates(data)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["unique_chunks"], 1)
        self.assertEqual(res.value["duplicate_groups"][0]["count"], 3)

    def test_dup_clean_invalid_type(self):
        engine = OmniDupCleanHashEngine()
        res = engine.detect_duplicates(["not_bytes"])
        self.assertFalse(res.is_ok())
        self.assertIn("not bytes", res.error)

    # 2. OmniParallelMergeSortEngine
    def test_merge_sort_success(self):
        engine = OmniParallelMergeSortEngine()
        res = engine.sort([3, 1, 4, 1, 5, 9, 2, 6])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["sorted"], [1, 1, 2, 3, 4, 5, 6, 9])
        self.assertTrue(res.value["max_tree_depth"] > 0)

    def test_merge_sort_empty(self):
        engine = OmniParallelMergeSortEngine()
        res = engine.sort([])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["sorted"], [])
        self.assertEqual(res.value["max_tree_depth"], 0)

    def test_merge_sort_already_sorted(self):
        engine = OmniParallelMergeSortEngine()
        res = engine.sort([1, 2, 3, 4, 5])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["sorted"], [1, 2, 3, 4, 5])

    def test_merge_sort_reverse(self):
        engine = OmniParallelMergeSortEngine()
        res = engine.sort([5, 4, 3, 2, 1])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["sorted"], [1, 2, 3, 4, 5])

    def test_merge_sort_single(self):
        engine = OmniParallelMergeSortEngine()
        res = engine.sort([42])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["sorted"], [42])

    # 3. OmniBiometricAuthLogicEngine
    def test_biometric_auth_match(self):
        engine = OmniBiometricAuthLogicEngine()
        v1 = [1.0, 0.0, 1.0]
        v2 = [0.9, 0.1, 1.0]
        res = engine.authenticate(v1, v2, 0.90)
        self.assertTrue(res.is_ok())
        self.assertTrue(res.value["authenticated"])
        self.assertTrue(res.value["similarity_score"] > 0.90)

    def test_biometric_auth_no_match(self):
        engine = OmniBiometricAuthLogicEngine()
        v1 = [1.0, 0.0, 0.0]
        v2 = [0.0, 1.0, 0.0]
        res = engine.authenticate(v1, v2, 0.5)
        self.assertTrue(res.is_ok())
        self.assertFalse(res.value["authenticated"])
        self.assertEqual(res.value["similarity_score"], 0.0)

    def test_biometric_auth_mismatch_dims(self):
        engine = OmniBiometricAuthLogicEngine()
        res = engine.authenticate([1.0, 2.0], [1.0], 0.5)
        self.assertFalse(res.is_ok())
        self.assertEqual(res.error, "Vector dimensions must match exactly")

    def test_biometric_auth_empty(self):
        engine = OmniBiometricAuthLogicEngine()
        res = engine.authenticate([], [], 0.5)
        self.assertFalse(res.is_ok())
        self.assertEqual(res.error, "Vectors cannot be empty")

    def test_biometric_auth_zero_vector(self):
        engine = OmniBiometricAuthLogicEngine()
        res = engine.authenticate([0.0, 0.0], [1.0, 1.0], 0.5)
        self.assertTrue(res.is_ok())
        self.assertFalse(res.value["authenticated"])
        self.assertEqual(res.value["similarity_score"], 0.0)

    # 4. OmniCourseAllocatorEngine
    def test_course_allocator_success(self):
        engine = OmniCourseAllocatorEngine()
        caps = {"MATH101": 1, "ENG101": 1}
        students = [
            {"id": "s1", "gpa": 3.0, "preferences": ["MATH101", "ENG101"]},
            {"id": "s2", "gpa": 4.0, "preferences": ["MATH101", "ENG101"]}
        ]
        res = engine.allocate(students, caps)
        self.assertTrue(res.is_ok())
        alloc = res.value["allocations"]
        self.assertEqual(alloc["s2"], "MATH101")
        self.assertEqual(alloc["s1"], "ENG101")
        self.assertEqual(res.value["remaining_capacities"]["MATH101"], 0)

    def test_course_allocator_waitlist(self):
        engine = OmniCourseAllocatorEngine()
        caps = {"CS101": 1}
        students = [
            {"id": "s1", "gpa": 3.0, "preferences": ["CS101"]},
            {"id": "s2", "gpa": 4.0, "preferences": ["CS101"]}
        ]
        res = engine.allocate(students, caps)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["allocations"]["s2"], "CS101")
        self.assertNotIn("s1", res.value["allocations"])
        self.assertIn("s1", res.value["waitlists"]["CS101"])

    def test_course_allocator_no_prefs(self):
        engine = OmniCourseAllocatorEngine()
        res = engine.allocate([{"id": "s1", "gpa": 3.5}], {"H": 10})
        self.assertTrue(res.is_ok())
        self.assertEqual(len(res.value["allocations"]), 0)

    def test_course_allocator_tie_breaker(self):
        engine = OmniCourseAllocatorEngine()
        students = [
            {"id": "2", "gpa": 3.5, "preferences": ["A"]},
            {"id": "1", "gpa": 3.5, "preferences": ["A"]}
        ]
        res = engine.allocate(students, {"A": 1})
        self.assertTrue(res.is_ok())
        # ID 1 should win tie breaker (sorted string ascending)
        self.assertEqual(res.value["allocations"]["1"], "A")
        self.assertNotIn("2", res.value["allocations"])

    def test_course_allocator_all_waitlisted(self):
        engine = OmniCourseAllocatorEngine()
        students = [{"id": "s1", "gpa": 4.0, "preferences": ["A"]}]
        res = engine.allocate(students, {"A": 0})
        self.assertTrue(res.is_ok())
        self.assertNotIn("s1", res.value["allocations"])
        self.assertIn("s1", res.value["waitlists"]["A"])

    # 5. OmniFitnessMetricsEngine
    def test_fitness_metrics_success(self):
        engine = OmniFitnessMetricsEngine()
        acts = [{"mets": 8.0, "duration_min": 30}]
        # 80 kg, 180 cm
        res = engine.calculate_metrics(80.0, 180.0, acts)
        self.assertTrue(res.is_ok())
        self.assertAlmostEqual(res.value["bmi"], 24.69, places=2)
        self.assertEqual(res.value["category"], "normal")
        self.assertAlmostEqual(res.value["bmr_estimation"], 80 * 24.0)
        self.assertAlmostEqual(res.value["active_calories_burned"], 8.0 * 80.0 * 0.5)

    def test_fitness_metrics_underweight(self):
        engine = OmniFitnessMetricsEngine()
        res = engine.calculate_metrics(50.0, 180.0, [])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["category"], "underweight")

    def test_fitness_metrics_obese(self):
        engine = OmniFitnessMetricsEngine()
        res = engine.calculate_metrics(120.0, 170.0, [])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["category"], "obese")

    def test_fitness_metrics_zero_weight(self):
        engine = OmniFitnessMetricsEngine()
        res = engine.calculate_metrics(0.0, 180.0, [])
        self.assertFalse(res.is_ok())
        self.assertEqual(res.error, "Weight and height must be strictly positive")

    def test_fitness_metrics_multiple_activities(self):
        engine = OmniFitnessMetricsEngine()
        acts = [
            {"mets": 3.0, "duration_min": 60},
            {"mets": 5.0, "duration_min": 30}
        ]
        res = engine.calculate_metrics(70.0, 175.0, acts)
        self.assertTrue(res.is_ok())
        expected_burn = (3.0 * 70.0 * 1.0) + (5.0 * 70.0 * 0.5)
        self.assertAlmostEqual(res.value["active_calories_burned"], expected_burn)

    # 6. OmniMedicationScheduleEngine
    def test_med_schedule_success(self):
        engine = OmniMedicationScheduleEngine()
        res = engine.generate_schedule(8, 8, 3)
        self.assertTrue(res.is_ok())
        sched = res.value["schedule"]
        self.assertEqual(len(sched), 3)
        self.assertEqual(sched[0]["time_24h"], "08:00")
        self.assertEqual(sched[0]["day_offset"], 0)
        self.assertEqual(sched[1]["time_24h"], "16:00")
        self.assertEqual(sched[1]["day_offset"], 0)
        self.assertEqual(sched[2]["time_24h"], "00:00")
        self.assertEqual(sched[2]["day_offset"], 1)

    def test_med_schedule_invalid_start(self):
        engine = OmniMedicationScheduleEngine()
        res = engine.generate_schedule(25, 8, 3)
        self.assertFalse(res.is_ok())
        self.assertIn("Start hour", res.error)

    def test_med_schedule_invalid_interval(self):
        engine = OmniMedicationScheduleEngine()
        res = engine.generate_schedule(8, 0, 3)
        self.assertFalse(res.is_ok())
        self.assertIn("Interval must be positive", res.error)

    def test_med_schedule_invalid_doses(self):
        engine = OmniMedicationScheduleEngine()
        res = engine.generate_schedule(8, 8, -1)
        self.assertFalse(res.is_ok())
        self.assertIn("Total doses must be positive", res.error)

    def test_med_schedule_long_span(self):
        engine = OmniMedicationScheduleEngine()
        res = engine.generate_schedule(10, 24, 5) # once a day
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["total_days_spanned"], 5)
        for i, s in enumerate(res.value["schedule"]):
            self.assertEqual(s["time_24h"], "10:00")
            self.assertEqual(s["day_offset"], i)

    # 7. OmniStaticSiteGeneratorEngine
    def test_ssg_success(self):
        engine = OmniStaticSiteGeneratorEngine()
        ast = {
            "tag": "html",
            "children": [
                {"tag": "body", "children": [
                    {"tag": "h1", "attributes": {"class": "title"}, "children": [{"text": "Hello"}]},
                    {"tag": "img", "attributes": {"src": "h.png"}}
                ]}
            ]
        }
        res = engine.generate_html(ast)
        self.assertTrue(res.is_ok())
        self.assertIn('<html><body><h1 class="title">Hello</h1><img src="h.png"></body></html>', res.value)

    def test_ssg_text_escape(self):
        engine = OmniStaticSiteGeneratorEngine()
        ast = {"tag": "p", "children": [{"text": "<script>alert(1)</script>"}]}
        res = engine.generate_html(ast)
        self.assertTrue(res.is_ok())
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", res.value)

    def test_ssg_void_element(self):
        engine = OmniStaticSiteGeneratorEngine()
        ast = {"tag": "hr", "attributes": {"class": "sep"}}
        res = engine.generate_html(ast)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value, '<hr class="sep">')

    def test_ssg_empty_div(self):
        engine = OmniStaticSiteGeneratorEngine()
        res = engine.generate_html({"tag": "div"})
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value, '<div></div>')

    def test_ssg_default_tag(self):
        engine = OmniStaticSiteGeneratorEngine()
        # Missing tag
        res = engine.generate_html({"children": [{"text": "default"}]})
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value, '<div>default</div>')

    # 8. OmniJobMatcherEngine
    def test_job_matcher_success(self):
        engine = OmniJobMatcherEngine()
        reqs = ["Python", "Docker"]
        apps = [
            {"id": 1, "skills": ["Python", "Java"]},
            {"id": 2, "skills": ["Python", "Docker", "AWS"]}
        ]
        res = engine.rank_applicants(reqs, apps)
        self.assertTrue(res.is_ok())
        ranks = res.value
        self.assertEqual(len(ranks), 2)
        # ID 2 should be first
        self.assertEqual(ranks[0]["applicant_id"], 2)
        self.assertEqual(ranks[0]["match_score"], 2/3) # IOU: Inter(Python, Docker) = 2, Union = (Python, Docker, AWS) = 3
        self.assertEqual(ranks[1]["applicant_id"], 1)
        self.assertEqual(ranks[1]["match_score"], 1/3) # Python only

    def test_job_matcher_no_skills(self):
        engine = OmniJobMatcherEngine()
        res = engine.rank_applicants([], [])
        self.assertFalse(res.is_ok())
        self.assertIn("required skill is needed", res.error)

    def test_job_matcher_empty_applicant(self):
        engine = OmniJobMatcherEngine()
        reqs = ["Python"]
        apps = [{"id": 1, "skills": []}]
        res = engine.rank_applicants(reqs, apps)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value[0]["match_score"], 0.0)

    def test_job_matcher_perfect_match(self):
        engine = OmniJobMatcherEngine()
        reqs = ["A", "b"]
        apps = [{"id": 1, "skills": ["a", "B"]}]
        res = engine.rank_applicants(reqs, apps)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value[0]["match_score"], 1.0)

    def test_job_matcher_tie_break(self):
        engine = OmniJobMatcherEngine()
        reqs = ["A"]
        apps = [
            {"id": "Z", "skills": ["A"]},
            {"id": "A", "skills": ["A"]}
        ]
        res = engine.rank_applicants(reqs, apps)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value[0]["applicant_id"], "A")
        self.assertEqual(res.value[1]["applicant_id"], "Z")

    # 9. OmniCustomStackCalculatorEngine
    def test_rpn_evaluate_success(self):
        engine = OmniCustomStackCalculatorEngine()
        # (3 + 4) * 5 = 35 -> 3 4 + 5 *
        res = engine.evaluate_rpn([3, 4, "+", 5, "*"])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value, 35.0)

    def test_rpn_evaluate_division(self):
        engine = OmniCustomStackCalculatorEngine()
        # 10 / 2 = 5
        res = engine.evaluate_rpn([10, 2, "/"])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value, 5.0)

    def test_rpn_evaluate_div_zero(self):
        engine = OmniCustomStackCalculatorEngine()
        res = engine.evaluate_rpn([1, 0, "/"])
        self.assertFalse(res.is_ok())
        self.assertIn("Division by zero", res.error)

    def test_rpn_evaluate_insufficient_operands(self):
        engine = OmniCustomStackCalculatorEngine()
        res = engine.evaluate_rpn([1, "+"])
        self.assertFalse(res.is_ok())
        self.assertIn("Insufficient", res.error)

    def test_rpn_evaluate_invalid_token(self):
        engine = OmniCustomStackCalculatorEngine()
        res = engine.evaluate_rpn([1, 2, "^"])
        self.assertFalse(res.is_ok())
        self.assertIn("Unknown operator", res.error)

    def test_rpn_evaluate_leftovers(self):
        engine = OmniCustomStackCalculatorEngine()
        res = engine.evaluate_rpn([1, 2, "+", 3])
        self.assertFalse(res.is_ok())
        self.assertIn("left on stack", res.error)

    # 10. OmniProjectScaffoldEngine
    def test_scaffold_web_app(self):
        engine = OmniProjectScaffoldEngine()
        res = engine.generate_manifest("myapp", "web_app")
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["manifest"]["name"], "myapp")
        children = [c["name"] for c in res.value["manifest"]["children"]]
        self.assertIn("src", children)
        self.assertIn("package.json", children)

    def test_scaffold_cli_tool(self):
        engine = OmniProjectScaffoldEngine()
        res = engine.generate_manifest("mycli", "cli_tool")
        self.assertTrue(res.is_ok())
        children = [c["name"] for c in res.value["manifest"]["children"]]
        self.assertIn("bin", children)
        self.assertIn("pyproject.toml", children)

    def test_scaffold_invalid_type(self):
        engine = OmniProjectScaffoldEngine()
        res = engine.generate_manifest("test", "mobile_app")
        self.assertFalse(res.is_ok())
        self.assertIn("Unknown template", res.error)

    def test_scaffold_empty_name(self):
        engine = OmniProjectScaffoldEngine()
        res = engine.generate_manifest("", "web_app")
        self.assertFalse(res.is_ok())
        self.assertIn("cannot be empty", res.error)

    def test_scaffold_nested_structure(self):
        engine = OmniProjectScaffoldEngine()
        res = engine.generate_manifest("t", "web_app")
        self.assertTrue(res.is_ok())
        src_dir = next(c for c in res.value["manifest"]["children"] if c["name"] == "src")
        src_children = [c["name"] for c in src_dir["children"]]
        self.assertIn("index.html", src_children)

if __name__ == '__main__':
    unittest.main()
