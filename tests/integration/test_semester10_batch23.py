"""Integration test suite for Semester 10 — Batch 23.

Covers all 5 engines:
1. OmniFieldenmsTgEntityValidationEngine — schema-driven entity property validation
2. OmniGoalkitOutcomeTrackingEngine — weighted goal tree progress aggregation
3. OmniOpenGenusTradingOrderBookEngine — price-time priority order matching
4. OmniPycodarCodebaseMetricsEngine — recursive file tree metrics aggregation
5. OmniDocrunnerCodeblockValidatorEngine — markdown code block extraction & validation
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.compute.python_core.omni_fieldenms_tg_entity_validation_engine import OmniFieldenmsTgEntityValidationEngine
from src.compute.python_core.omni_goalkit_outcome_tracking_engine import OmniGoalkitOutcomeTrackingEngine
from src.compute.python_core.omni_opengenus_trading_orderbook_engine import OmniOpenGenusTradingOrderBookEngine
from src.compute.python_core.omni_pycodar_codebase_metrics_engine import OmniPycodarCodebaseMetricsEngine
from src.compute.python_core.omni_docrunner_codeblock_validator_engine import OmniDocrunnerCodeblockValidatorEngine

# ===================================================================
# 1. OmniFieldenmsTgEntityValidationEngine
# ===================================================================
class TestFieldenmsTgEntityValidation:
    SCHEMA = [
        {"name": "id", "type": "int", "required": True, "min": 1},
        {"name": "name", "type": "str", "required": True, "min_length": 2, "max_length": 50},
        {"name": "email", "type": "str", "required": True, "pattern": r"^[\w.+-]+@[\w-]+\.[\w.]+$"},
        {"name": "age", "type": "int", "required": False, "min": 0, "max": 150},
        {"name": "active", "type": "bool", "required": False},
    ]

    def test_diagnostics(self):
        d = OmniFieldenmsTgEntityValidationEngine.diagnostics()
        assert d["engine"] == "OmniFieldenmsTgEntityValidationEngine"
        assert d["monadic_enforcement"] is True

    def test_valid_entity(self):
        entity = {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30, "active": True}
        result = OmniFieldenmsTgEntityValidationEngine.validate_entity(self.SCHEMA, entity)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        data = result.unwrap()
        assert data["valid"] is True
        assert len(data["errors"]) == 0

    def test_missing_required_field(self):
        entity = {"id": 1, "name": "Bob"}  # missing email
        result = OmniFieldenmsTgEntityValidationEngine.validate_entity(self.SCHEMA, entity)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        data = result.unwrap()
        assert data["valid"] is False
        assert any("email" in e and "required" in e for e in data["errors"])

    def test_type_mismatch(self):
        entity = {"id": "not_int", "name": "Bob", "email": "bob@test.com"}
        result = OmniFieldenmsTgEntityValidationEngine.validate_entity(self.SCHEMA, entity)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        data = result.unwrap()
        assert data["valid"] is False
        assert any("expected type" in e for e in data["errors"])

    def test_range_violation(self):
        entity = {"id": 1, "name": "Charlie", "email": "c@d.com", "age": 200}
        result = OmniFieldenmsTgEntityValidationEngine.validate_entity(self.SCHEMA, entity)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        assert result.unwrap()["valid"] is False

    def test_pattern_violation(self):
        entity = {"id": 1, "name": "Dave", "email": "not-an-email"}
        result = OmniFieldenmsTgEntityValidationEngine.validate_entity(self.SCHEMA, entity)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        assert result.unwrap()["valid"] is False

    def test_string_length_violation(self):
        entity = {"id": 1, "name": "A", "email": "a@b.com"}  # name too short
        result = OmniFieldenmsTgEntityValidationEngine.validate_entity(self.SCHEMA, entity)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        assert result.unwrap()["valid"] is False

    def test_relationship_validation_ok(self):
        entities = {"e1": {}, "e2": {}, "e3": {}}
        rels = [("e1", "e2"), ("e2", "e3")]
        result = OmniFieldenmsTgEntityValidationEngine.validate_entity_relationships(entities, rels)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        assert result.unwrap()["valid"] is True

    def test_relationship_broken_ref(self):
        entities = {"e1": {}}
        rels = [("e1", "e99")]
        result = OmniFieldenmsTgEntityValidationEngine.validate_entity_relationships(entities, rels)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        data = result.unwrap()
        assert data["valid"] is False
        assert len(data["broken_refs"]) == 1


# ===================================================================
# 2. OmniGoalkitOutcomeTrackingEngine
# ===================================================================
class TestGoalkitOutcomeTracking:
    GOAL_TREE = {
        "name": "Release v2.0",
        "weight": 1.0,
        "status": "in_progress",
        "children": [
            {"name": "Backend API", "weight": 3.0, "status": "done", "children": []},
            {"name": "Frontend UI", "weight": 2.0, "status": "in_progress", "children": []},
            {"name": "Testing", "weight": 2.0, "status": "todo", "children": []},
            {"name": "Docs", "weight": 1.0, "status": "blocked", "children": []},
        ],
    }

    def test_diagnostics(self):
        d = OmniGoalkitOutcomeTrackingEngine.diagnostics()
        assert d["engine"] == "OmniGoalkitOutcomeTrackingEngine"
        assert d["monadic_enforcement"] is True

    def test_goal_progress(self):
        result = OmniGoalkitOutcomeTrackingEngine.compute_goal_progress(self.GOAL_TREE)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        data = result.unwrap()
        # Backend(3.0 done) + Frontend(2.0*0.5) + Testing(0) + Docs(0) = 4.0/8.0 = 0.5
        assert abs(data["progress"] - 0.5) < 0.001
        assert data["total_tasks"] == 4
        assert data["completed_tasks"] == 1
        assert data["blocked_tasks"] == 1

    def test_all_done(self):
        tree = {"name": "Simple", "weight": 1.0, "status": "done", "children": []}
        result = OmniGoalkitOutcomeTrackingEngine.compute_goal_progress(tree)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        assert result.unwrap()["progress"] == 1.0

    def test_deadline_feasible(self):
        result = OmniGoalkitOutcomeTrackingEngine.evaluate_deadline_feasibility(
            total_tasks=100, completed_tasks=60, days_elapsed=30, days_remaining=20
        )
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        data = result.unwrap()
        # velocity = 60/30 = 2.0, required = 40/20 = 2.0 => feasible
        assert data["feasible"] is True
        assert data["velocity"] == 2.0

    def test_deadline_not_feasible(self):
        result = OmniGoalkitOutcomeTrackingEngine.evaluate_deadline_feasibility(
            total_tasks=100, completed_tasks=20, days_elapsed=30, days_remaining=5
        )
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        data = result.unwrap()
        assert data["feasible"] is False

    def test_invalid_tasks(self):
        result = OmniGoalkitOutcomeTrackingEngine.evaluate_deadline_feasibility(
            total_tasks=0, completed_tasks=0, days_elapsed=0, days_remaining=0
        )
        assert not result.is_ok()


# ===================================================================
# 3. OmniOpenGenusTradingOrderBookEngine
# ===================================================================
class TestOpenGenusTradingOrderBook:
    BIDS = [
        {"price": 100.0, "qty": 10, "timestamp": 1},
        {"price": 99.5, "qty": 20, "timestamp": 2},
        {"price": 99.0, "qty": 15, "timestamp": 3},
    ]
    ASKS = [
        {"price": 101.0, "qty": 10, "timestamp": 1},
        {"price": 101.5, "qty": 20, "timestamp": 2},
        {"price": 102.0, "qty": 5, "timestamp": 3},
    ]

    def test_diagnostics(self):
        d = OmniOpenGenusTradingOrderBookEngine.diagnostics()
        assert d["engine"] == "OmniOpenGenusTradingOrderBookEngine"
        assert d["monadic_enforcement"] is True

    def test_spread(self):
        result = OmniOpenGenusTradingOrderBookEngine.compute_spread(self.BIDS, self.ASKS)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        data = result.unwrap()
        assert data["best_bid"] == 100.0
        assert data["best_ask"] == 101.0
        assert data["spread"] == 1.0
        assert data["mid_price"] == 100.5

    def test_spread_no_bids(self):
        result = OmniOpenGenusTradingOrderBookEngine.compute_spread([], self.ASKS)
        assert not result.is_ok()

    def test_buy_order_match(self):
        order = {"side": "buy", "price": 101.5, "qty": 15, "timestamp": 10}
        result = OmniOpenGenusTradingOrderBookEngine.match_order(order, self.BIDS, self.ASKS)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        data = result.unwrap()
        # Should match ask@101.0 (10 qty) + ask@101.5 (5 qty)
        assert data["fully_filled"] is True
        assert data["remaining_qty"] == 0
        assert len(data["fills"]) == 2

    def test_sell_order_match(self):
        order = {"side": "sell", "price": 99.0, "qty": 5, "timestamp": 10}
        result = OmniOpenGenusTradingOrderBookEngine.match_order(order, self.BIDS, self.ASKS)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        data = result.unwrap()
        assert data["fully_filled"] is True
        assert data["fills"][0]["price"] == 100.0  # best bid first

    def test_no_match(self):
        order = {"side": "buy", "price": 90.0, "qty": 10, "timestamp": 10}
        result = OmniOpenGenusTradingOrderBookEngine.match_order(order, self.BIDS, self.ASKS)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        assert result.unwrap()["remaining_qty"] == 10

    def test_vwap(self):
        trades = [
            {"price": 100.0, "qty": 10},
            {"price": 101.0, "qty": 20},
            {"price": 102.0, "qty": 10},
        ]
        result = OmniOpenGenusTradingOrderBookEngine.compute_vwap(trades)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        # (100*10 + 101*20 + 102*10) / 40 = 4040/40 = 101.0
        assert result.unwrap() == 101.0

    def test_vwap_empty(self):
        result = OmniOpenGenusTradingOrderBookEngine.compute_vwap([])
        assert not result.is_ok()


# ===================================================================
# 4. OmniPycodarCodebaseMetricsEngine
# ===================================================================
class TestPycodarCodebaseMetrics:
    FILE_TREE = [
        {"path": "src/main.py", "lines": 200, "functions": 10, "classes": 2},
        {"path": "src/utils.py", "lines": 50, "functions": 5, "classes": 0},
        {"path": "src/config.py", "lines": 20, "functions": 0, "classes": 0},
        {"path": "tests/test_main.py", "lines": 150, "functions": 8, "classes": 1},
    ]

    def test_diagnostics(self):
        d = OmniPycodarCodebaseMetricsEngine.diagnostics()
        assert d["engine"] == "OmniPycodarCodebaseMetricsEngine"
        assert d["monadic_enforcement"] is True

    def test_compute_metrics(self):
        result = OmniPycodarCodebaseMetricsEngine.compute_metrics(self.FILE_TREE)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        data = result.unwrap()
        assert data["total_files"] == 4
        assert data["total_lines"] == 420
        assert data["total_functions"] == 23
        assert data["total_classes"] == 3
        assert data["avg_lines_per_file"] == 105.0
        assert data["largest_file"]["path"] == "src/main.py"
        assert data["smallest_file"]["path"] == "src/config.py"

    def test_dead_code_candidates(self):
        result = OmniPycodarCodebaseMetricsEngine.detect_dead_code_candidates(self.FILE_TREE)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        candidates = result.unwrap()
        assert "src/config.py" in candidates
        assert "src/main.py" not in candidates

    def test_directory_depth(self):
        paths = ["src/core/engine/main.py", "src/utils.py", "README.md"]
        result = OmniPycodarCodebaseMetricsEngine.compute_directory_depth(paths)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        assert result.unwrap() == 3  # src/core/engine/main.py

    def test_empty_file_tree(self):
        result = OmniPycodarCodebaseMetricsEngine.compute_metrics([])
        assert not result.is_ok()


# ===================================================================
# 5. OmniDocrunnerCodeblockValidatorEngine
# ===================================================================
class TestDocrunnerCodeblockValidator:
    MARKDOWN = """# Example Documentation

Here is a Python example:

```python
def hello():
    print("Hello, World!")
```

And a JavaScript example:

```javascript
console.log("Hello!");
```

Another Python block:

```python
x = 42
```
"""

    def test_diagnostics(self):
        d = OmniDocrunnerCodeblockValidatorEngine.diagnostics()
        assert d["engine"] == "OmniDocrunnerCodeblockValidatorEngine"
        assert d["monadic_enforcement"] is True

    def test_extract_blocks(self):
        result = OmniDocrunnerCodeblockValidatorEngine.extract_code_blocks(self.MARKDOWN)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        blocks = result.unwrap()
        assert len(blocks) == 3
        assert blocks[0]["language"] == "python"
        assert blocks[1]["language"] == "javascript"

    def test_validate_required_languages_pass(self):
        blocks = [{"language": "python"}, {"language": "javascript"}]
        result = OmniDocrunnerCodeblockValidatorEngine.validate_required_languages(
            blocks, ["python", "javascript"]
        )
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        assert result.unwrap()["valid"] is True

    def test_validate_required_languages_fail(self):
        blocks = [{"language": "python"}]
        result = OmniDocrunnerCodeblockValidatorEngine.validate_required_languages(
            blocks, ["python", "rust"]
        )
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        data = result.unwrap()
        assert data["valid"] is False
        assert "rust" in data["missing_languages"]

    def test_coverage_score(self):
        result = OmniDocrunnerCodeblockValidatorEngine.compute_coverage(10, 8)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        assert result.unwrap()["coverage"] == 0.8

    def test_coverage_zero_blocks(self):
        result = OmniDocrunnerCodeblockValidatorEngine.compute_coverage(0, 0)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        assert result.unwrap()["coverage"] == 1.0

    def test_detect_duplicates(self):
        blocks = [
            {"code": "print('hi')"},
            {"code": "x = 1"},
            {"code": "print('hi')"},
        ]
        result = OmniDocrunnerCodeblockValidatorEngine.detect_duplicates(blocks)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        dups = result.unwrap()
        assert len(dups) == 1
        assert 0 in dups[0] and 2 in dups[0]

    def test_no_duplicates(self):
        blocks = [{"code": "a"}, {"code": "b"}, {"code": "c"}]
        result = OmniDocrunnerCodeblockValidatorEngine.detect_duplicates(blocks)
        assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
        assert len(result.unwrap()) == 0

    def test_empty_markdown(self):
        result = OmniDocrunnerCodeblockValidatorEngine.extract_code_blocks("")
        assert not result.is_ok()
