import unittest
from src.compute.python_core.omni_shell_lexer_engine import OmniShellLexerEngine
from src.compute.python_core.omni_library_penalty_engine import OmniLibraryPenaltyEngine
from src.compute.python_core.omni_event_capacity_optimizer_engine import OmniEventCapacityOptimizerEngine
from src.compute.python_core.omni_dag_prerequisite_engine import OmniDagPrerequisiteEngine
from src.compute.python_core.omni_degree_audit_engine import OmniDegreeAuditEngine
from src.compute.python_core.omni_timetable_conflict_engine import OmniTimetableConflictEngine
from src.compute.python_core.omni_avl_tree_engine import OmniAvlTreeEngine
from src.compute.python_core.omni_sql_string_validator_engine import OmniSqlStringValidatorEngine
from src.compute.python_core.omni_spec_completeness_engine import OmniSpecCompletenessEngine
from src.compute.python_core.omni_glossary_trie_engine import OmniGlossaryTrieEngine

class TestSemester11Batch30(unittest.TestCase):
    # ---------------------------------------------------------
    # OmniShellLexerEngine (5 tests)
    # ---------------------------------------------------------
    def test_lexer_simple(self):
        engine = OmniShellLexerEngine()
        res = engine.tokenize("ls -la")
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["tokens"], ["ls", "-la"])

    def test_lexer_single_quotes(self):
        engine = OmniShellLexerEngine()
        res = engine.tokenize("echo 'hello world'")
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["tokens"], ["echo", "hello world"])

    def test_lexer_double_quotes(self):
        engine = OmniShellLexerEngine()
        res = engine.tokenize('grep "foo bar" file.txt')
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["tokens"], ["grep", "foo bar", "file.txt"])

    def test_lexer_operators(self):
        engine = OmniShellLexerEngine()
        res = engine.tokenize("cat foo.txt > bar.txt")
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["tokens"], ["cat", "foo.txt", ">", "bar.txt"])

    def test_lexer_unclosed_quotes(self):
        engine = OmniShellLexerEngine()
        res = engine.tokenize("echo 'hi")
        self.assertFalse(res.is_ok())
        self.assertEqual(res.error, "Unclosed quote detected in command")

    # ---------------------------------------------------------
    # OmniLibraryPenaltyEngine (5 tests)
    # ---------------------------------------------------------
    def test_penalty_zero_days(self):
        engine = OmniLibraryPenaltyEngine()
        res = engine.calculate_penalty(0, 1.0, 100.0, 1.0)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["penalty_applied"], 0.0)

    def test_penalty_flat_rate(self):
        engine = OmniLibraryPenaltyEngine()
        res = engine.calculate_penalty(5, 2.0, 100.0, 1.0)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["penalty_applied"], 10.0)

    def test_penalty_compound_rate(self):
        engine = OmniLibraryPenaltyEngine()
        res = engine.calculate_penalty(3, 1.0, 100.0, 2.0)
        self.assertTrue(res.is_ok())
        # a=1, r=2, n=3 => 1*(2^3 - 1)/(2-1) = 7
        self.assertEqual(res.value["penalty_applied"], 7.0)

    def test_penalty_capped_at_max(self):
        engine = OmniLibraryPenaltyEngine()
        res = engine.calculate_penalty(10, 5.0, 20.0, 1.0)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["penalty_applied"], 20.0)
        self.assertTrue(res.value["is_maxed"])

    def test_penalty_negative_days(self):
        engine = OmniLibraryPenaltyEngine()
        res = engine.calculate_penalty(-1, 1.0, 100.0, 1.0)
        self.assertFalse(res.is_ok())
        self.assertEqual(res.error, "Days late cannot be negative")

    # ---------------------------------------------------------
    # OmniEventCapacityOptimizerEngine (5 tests)
    # ---------------------------------------------------------
    def test_knapsack_standard(self):
        engine = OmniEventCapacityOptimizerEngine()
        groups = [{"size": 10, "value": 60}, {"size": 20, "value": 100}, {"size": 30, "value": 120}]
        res = engine.optimize(50, groups)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["maximized_value"], 220) # 60 + 120 ? no, 10+20+30? 50 can fit 20 and 30 = 220.

    def test_knapsack_exact_capacity(self):
        engine = OmniEventCapacityOptimizerEngine()
        groups = [{"size": 5, "value": 10}, {"size": 5, "value": 10}]
        res = engine.optimize(10, groups)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["maximized_value"], 20)
        self.assertEqual(res.value["total_size_used"], 10)

    def test_knapsack_over_capacity(self):
        engine = OmniEventCapacityOptimizerEngine()
        groups = [{"size": 100, "value": 500}]
        res = engine.optimize(50, groups)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["maximized_value"], 0)
        self.assertEqual(res.value["total_size_used"], 0)

    def test_knapsack_empty_groups(self):
        engine = OmniEventCapacityOptimizerEngine()
        res = engine.optimize(50, [])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["maximized_value"], 0)

    def test_knapsack_negative_capacity(self):
        engine = OmniEventCapacityOptimizerEngine()
        res = engine.optimize(-5, [{"size": 5, "value": 10}])
        self.assertFalse(res.is_ok())
        self.assertEqual(res.error, "Capacity cannot be negative")

    # ---------------------------------------------------------
    # OmniDagPrerequisiteEngine (5 tests)
    # ---------------------------------------------------------
    def test_dag_linear(self):
        engine = OmniDagPrerequisiteEngine()
        res = engine.resolve_order(["A", "B", "C"], [("A", "B"), ("B", "C")])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["resolved_order"], ["A", "B", "C"])

    def test_dag_multiple_deps(self):
        engine = OmniDagPrerequisiteEngine()
        res = engine.resolve_order(["A", "B", "C", "D"], [("A", "C"), ("B", "C"), ("C", "D")])
        self.assertTrue(res.is_ok())
        # A and B have 0 in-degree. Alphabetical pop means A then B.
        self.assertEqual(res.value["resolved_order"], ["A", "B", "C", "D"])

    def test_dag_disconnected(self):
        engine = OmniDagPrerequisiteEngine()
        res = engine.resolve_order(["A", "B", "C"], [])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["resolved_order"], ["A", "B", "C"])

    def test_dag_cycle_detection(self):
        engine = OmniDagPrerequisiteEngine()
        res = engine.resolve_order(["A", "B", "C"], [("A", "B"), ("B", "C"), ("C", "A")])
        self.assertFalse(res.is_ok())
        self.assertEqual(res.error, "Cycle detected: Prerequisites form a closed loop")

    def test_dag_unknown_course(self):
        engine = OmniDagPrerequisiteEngine()
        res = engine.resolve_order(["A", "B"], [("A", "Z")])
        self.assertFalse(res.is_ok())
        self.assertEqual(res.error, "Unknown course in prereqs: A -> Z")

    # ---------------------------------------------------------
    # OmniDegreeAuditEngine (5 tests)
    # ---------------------------------------------------------
    def test_audit_sufficient_credits(self):
        engine = OmniDegreeAuditEngine()
        completed = [{"id": "CS101", "category": "CORE", "credits": 4}]
        rules = {"CORE": 3}
        res = engine.audit(completed, rules)
        self.assertTrue(res.is_ok())
        self.assertTrue(res.value["eligible_for_graduation"])

    def test_audit_insufficient_credits(self):
        engine = OmniDegreeAuditEngine()
        completed = [{"id": "CS101", "category": "CORE", "credits": 2}]
        rules = {"CORE": 4}
        res = engine.audit(completed, rules)
        self.assertTrue(res.is_ok())
        self.assertFalse(res.value["eligible_for_graduation"])
        self.assertEqual(res.value["deficiencies"]["CORE"], 2)

    def test_audit_multiple_categories(self):
        engine = OmniDegreeAuditEngine()
        completed = [
            {"id": "CS101", "category": "CORE", "credits": 4},
            {"id": "ART101", "category": "ELEC", "credits": 3}
        ]
        rules = {"CORE": 4, "ELEC": 3}
        res = engine.audit(completed, rules)
        self.assertTrue(res.is_ok())
        self.assertTrue(res.value["eligible_for_graduation"])

    def test_audit_missing_category_entirely(self):
        engine = OmniDegreeAuditEngine()
        completed = [{"id": "CS101", "category": "CORE", "credits": 4}]
        rules = {"CORE": 4, "ELEC": 3}
        res = engine.audit(completed, rules)
        self.assertTrue(res.is_ok())
        self.assertFalse(res.value["eligible_for_graduation"])
        self.assertEqual(res.value["deficiencies"]["ELEC"], 3)

    def test_audit_invalid_input(self):
        engine = OmniDegreeAuditEngine()
        res = engine.audit([], "not a dict")
        self.assertFalse(res.is_ok())
        self.assertEqual(res.error, "Invalid input types")

    # ---------------------------------------------------------
    # OmniTimetableConflictEngine (5 tests)
    # ---------------------------------------------------------
    def test_conflict_no_overlap(self):
        engine = OmniTimetableConflictEngine()
        schedules = [
            {"id": "c1", "start": 900, "end": 1000},
            {"id": "c2", "start": 1000, "end": 1100}
        ]
        res = engine.detect_conflicts(schedules)
        self.assertTrue(res.is_ok())
        self.assertFalse(res.value["has_conflict"])

    def test_conflict_with_overlap(self):
        engine = OmniTimetableConflictEngine()
        schedules = [
            {"id": "c1", "start": 900, "end": 1030},
            {"id": "c2", "start": 1000, "end": 1100}
        ]
        res = engine.detect_conflicts(schedules)
        self.assertTrue(res.is_ok())
        self.assertTrue(res.value["has_conflict"])
        self.assertEqual(len(res.value["conflicts"]), 1)

    def test_conflict_nested(self):
        engine = OmniTimetableConflictEngine()
        schedules = [
            {"id": "c1", "start": 900, "end": 1200},
            {"id": "c2", "start": 1000, "end": 1100}
        ]
        res = engine.detect_conflicts(schedules)
        self.assertTrue(res.is_ok())
        self.assertTrue(res.value["has_conflict"])

    def test_conflict_invalid_interval(self):
        engine = OmniTimetableConflictEngine()
        schedules = [{"id": "c1", "start": 1000, "end": 900}]
        res = engine.detect_conflicts(schedules)
        self.assertFalse(res.is_ok())

    def test_conflict_missing_keys(self):
        engine = OmniTimetableConflictEngine()
        schedules = [{"start": 900, "end": 1000}]
        res = engine.detect_conflicts(schedules)
        self.assertFalse(res.is_ok())

    # ---------------------------------------------------------
    # OmniAvlTreeEngine (5 tests)
    # ---------------------------------------------------------
    def test_avl_insert_and_balance_ll(self):
        engine = OmniAvlTreeEngine()
        res = engine.build_and_traverse([30, 20, 10])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["in_order"], [10, 20, 30])
        self.assertEqual(res.value["pre_order"], [20, 10, 30])
        self.assertEqual(res.value["depth"], 2)

    def test_avl_insert_and_balance_rr(self):
        engine = OmniAvlTreeEngine()
        res = engine.build_and_traverse([10, 20, 30])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["pre_order"], [20, 10, 30])

    def test_avl_insert_and_balance_lr(self):
        engine = OmniAvlTreeEngine()
        res = engine.build_and_traverse([30, 10, 20])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["pre_order"], [20, 10, 30])

    def test_avl_insert_and_balance_rl(self):
        engine = OmniAvlTreeEngine()
        res = engine.build_and_traverse([10, 30, 20])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["pre_order"], [20, 10, 30])

    def test_avl_duplicates_ignored(self):
        engine = OmniAvlTreeEngine()
        res = engine.build_and_traverse([10, 10, 10])
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value["in_order"], [10])

    # ---------------------------------------------------------
    # OmniSqlStringValidatorEngine (5 tests)
    # ---------------------------------------------------------
    def test_sql_valid_select(self):
        engine = OmniSqlStringValidatorEngine()
        res = engine.validate("SELECT id, name FROM users")
        self.assertTrue(res.is_ok())
        self.assertTrue(res.value["is_valid_structure"])
        self.assertTrue(res.value["is_safe"])
        self.assertEqual(res.value["table"], "USERS")

    def test_sql_valid_select_where(self):
        engine = OmniSqlStringValidatorEngine()
        res = engine.validate("SELECT id FROM users WHERE age > 18;")
        self.assertTrue(res.is_ok())
        self.assertTrue(res.value["is_valid_structure"])
        self.assertEqual(res.value["where_clause"], "AGE > 18")

    def test_sql_dangerous_keyword(self):
        engine = OmniSqlStringValidatorEngine()
        res = engine.validate("SELECT id FROM users; DROP TABLE users;")
        self.assertTrue(res.is_ok())
        self.assertFalse(res.value["is_safe"])
        self.assertIn("DROP", res.value["dangerous_keywords_found"])

    def test_sql_invalid_structure(self):
        engine = OmniSqlStringValidatorEngine()
        res = engine.validate("INSERT INTO users VALUES (1, 'john')")
        self.assertTrue(res.is_ok())
        self.assertFalse(res.value["is_valid_structure"])

    def test_sql_not_string(self):
        engine = OmniSqlStringValidatorEngine()
        res = engine.validate(123)
        self.assertFalse(res.is_ok())
        self.assertEqual(res.error, "SQL query must be a string")

    # ---------------------------------------------------------
    # OmniSpecCompletenessEngine (5 tests)
    # ---------------------------------------------------------
    def test_spec_complete(self):
        engine = OmniSpecCompletenessEngine()
        spec = {"name": "Bob", "age": 30}
        res = engine.check_spec(spec, ["name", "age"])
        self.assertTrue(res.is_ok())
        self.assertTrue(res.value["is_complete"])

    def test_spec_missing_fields(self):
        engine = OmniSpecCompletenessEngine()
        spec = {"name": "Bob"}
        res = engine.check_spec(spec, ["name", "age"])
        self.assertTrue(res.is_ok())
        self.assertFalse(res.value["is_complete"])
        self.assertIn("age", res.value["missing_fields"])

    def test_spec_type_matching(self):
        engine = OmniSpecCompletenessEngine()
        spec = {"name": "Bob", "age": 30}
        type_map = {"name": "str", "age": "int"}
        res = engine.check_spec(spec, ["name", "age"], type_map)
        self.assertTrue(res.is_ok())
        self.assertTrue(res.value["is_complete"])

    def test_spec_type_mismatch(self):
        engine = OmniSpecCompletenessEngine()
        spec = {"name": "Bob", "age": "thirty"}
        type_map = {"name": "str", "age": "int"}
        res = engine.check_spec(spec, ["name", "age"], type_map)
        self.assertTrue(res.is_ok())
        self.assertFalse(res.value["is_complete"])
        self.assertIn("age", res.value["type_mismatches"])

    def test_spec_invalid_inputs(self):
        engine = OmniSpecCompletenessEngine()
        res = engine.check_spec("not a dict", [])
        self.assertFalse(res.is_ok())

    # ---------------------------------------------------------
    # OmniGlossaryTrieEngine (5 tests)
    # ---------------------------------------------------------
    def test_trie_insert_and_exact_search(self):
        engine = OmniGlossaryTrieEngine()
        engine.insert("apple", "A fruit")
        res = engine.search_exact("apple")
        self.assertTrue(res.is_ok())
        self.assertTrue(res.value["found"])
        self.assertEqual(res.value["definition"], "A fruit")

    def test_trie_search_not_found(self):
        engine = OmniGlossaryTrieEngine()
        engine.insert("apple", "A fruit")
        res = engine.search_exact("banana")
        self.assertTrue(res.is_ok())
        self.assertFalse(res.value["found"])

    def test_trie_prefix_search_multiple(self):
        engine = OmniGlossaryTrieEngine()
        engine.insert("apple", "A fruit")
        engine.insert("app", "Application")
        engine.insert("apricot", "Another fruit")
        engine.insert("banana", "Yellow fruit")
        
        res = engine.get_words_with_prefix("ap")
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value, ["app", "apple", "apricot"])

    def test_trie_prefix_no_match(self):
        engine = OmniGlossaryTrieEngine()
        engine.insert("apple", "A fruit")
        res = engine.get_words_with_prefix("b")
        self.assertTrue(res.is_ok())
        self.assertEqual(res.value, [])

    def test_trie_search_partial_word_as_exact(self):
        engine = OmniGlossaryTrieEngine()
        engine.insert("apple", "A fruit")
        # "app" is a prefix, but not an exact word in this context
        res = engine.search_exact("app")
        self.assertTrue(res.is_ok())
        self.assertFalse(res.value["found"])

    # ---------------------------------------------------------
    # Diagnostics Check (1 test)
    # ---------------------------------------------------------
    def test_all_diagnostics(self):
        engines = [
            OmniShellLexerEngine(), OmniLibraryPenaltyEngine(),
            OmniEventCapacityOptimizerEngine(), OmniDagPrerequisiteEngine(),
            OmniDegreeAuditEngine(), OmniTimetableConflictEngine(),
            OmniAvlTreeEngine(), OmniSqlStringValidatorEngine(),
            OmniSpecCompletenessEngine(), OmniGlossaryTrieEngine()
        ]
        count = 0
        for eng in engines:
            diag = eng.diagnostics()
            self.assertEqual(diag["status"], "operational")
            self.assertIn("engine", diag)
            count += 1
        self.assertEqual(count, 10)

if __name__ == '__main__':
    unittest.main()
