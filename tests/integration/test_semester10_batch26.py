import pytest
from src.compute.python_core.omni_firebase_rbac_engine import OmniFirebaseRBACEngine
from src.compute.python_core.omni_ddd_cart_checkout_engine import OmniDDDCartCheckoutEngine
from src.compute.python_core.omni_sme_inventory_eoq_engine import OmniSMEInventoryEOQEngine
from src.compute.python_core.omni_prompt_token_budget_engine import OmniPromptTokenBudgetEngine
from src.compute.python_core.omni_escape_room_state_engine import OmniEscapeRoomStateEngine

# --- OmniFirebaseRBACEngine Tests ---
class TestFirebaseRBAC:
    @pytest.fixture
    def engine(self):
        role_hierarchy = {
            "admin": ["editor", "auditor"],
            "editor": ["viewer"],
            "auditor": ["viewer"]
        }
        resource_rules = {
            "reports": {
                "read": ["viewer"],
                "write": ["editor"],
                "delete": ["admin"]
            },
            "financials": {
                "read": ["auditor"],
                "write": ["admin"]
            }
        }
        return OmniFirebaseRBACEngine(role_hierarchy, resource_rules)

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()
        assert len(diag["roles_configured"]) == 3
        
    def test_admin_access(self, engine):
        # Admin inherits editor, auditor, viewer
        assert engine.evaluate_access(["admin"], "reports", "read").unwrap() is True
        assert engine.evaluate_access(["admin"], "reports", "write").unwrap() is True
        assert engine.evaluate_access(["admin"], "reports", "delete").unwrap() is True
        assert engine.evaluate_access(["admin"], "financials", "read").unwrap() is True

    def test_editor_access(self, engine):
        # Editor inherits viewer
        assert engine.evaluate_access(["editor"], "reports", "read").unwrap() is True
        assert engine.evaluate_access(["editor"], "reports", "write").unwrap() is True
        assert engine.evaluate_access(["editor"], "reports", "delete").unwrap() is False
        assert engine.evaluate_access(["editor"], "financials", "read").unwrap() is False

    def test_viewer_access(self, engine):
        # Viewer inherits nothing
        assert engine.evaluate_access(["viewer"], "reports", "read").unwrap() is True
        assert engine.evaluate_access(["viewer"], "reports", "write").unwrap() is False
        
    def test_generate_matrix(self, engine):
        matrix = engine.generate_access_matrix(["editor"]).unwrap()
        assert matrix["reports"]["write"] is True
        assert matrix["reports"]["delete"] is False
        assert matrix["financials"]["read"] is False

    def test_invalid_resource(self, engine):
        res = engine.evaluate_access(["admin"], "secrets", "read")
        assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))() is False


# --- OmniDDDCartCheckoutEngine Tests ---
class TestDDDCartCheckout:
    @pytest.fixture
    def engine(self):
        discount_tiers = {
            100.0: 0.10,
            50.0: 0.05
        }
        return OmniDDDCartCheckoutEngine(discount_tiers)

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()
        
    def test_valid_checkout_no_discount(self, engine):
        items = [{"price": 10.0, "qty": 2}]
        res = engine.process_checkout(items).unwrap()
        assert res["subtotal"] == 20.0
        assert res["discount_applied"] == 0.0
        assert res["final_total"] == 20.0
        
    def test_valid_checkout_tier_1_discount(self, engine):
        items = [{"price": 10.0, "qty": 6}] # $60
        res = engine.process_checkout(items).unwrap()
        assert res["subtotal"] == 60.0
        assert res["discount_applied"] == 3.0 # 5% of 60
        assert res["final_total"] == 57.0

    def test_valid_checkout_tier_2_discount(self, engine):
        items = [{"price": 50.0, "qty": 3}] # $150
        res = engine.process_checkout(items).unwrap()
        assert res["subtotal"] == 150.0
        assert res["discount_applied"] == 15.0 # 10% of 150
        assert res["final_total"] == 135.0

    def test_invalid_qty(self, engine):
        items = [{"price": 10.0, "qty": 0}]
        assert engine.process_checkout(items).is_ok() is False

    def test_negative_price(self, engine):
        items = [{"price": -5.0, "qty": 2}]
        assert engine.process_checkout(items).is_ok() is False

    def test_empty_cart(self, engine):
        assert engine.process_checkout([]).is_ok() is False


# --- OmniSMEInventoryEOQEngine Tests ---
class TestSMEInventoryEOQ:
    @pytest.fixture
    def engine(self):
        return OmniSMEInventoryEOQEngine(holding_cost_pct=0.20, operating_days_per_year=300)

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

    def test_compute_eoq(self, engine):
        # D = 1000, S = 50, C = 10, h = 0.2
        # H = 10 * 0.2 = 2
        # sqrt(2 * 1000 * 50 / 2) = sqrt(50000) = 223.6 -> 224
        eoq = engine.compute_eoq(1000, 50.0, 10.0).unwrap()
        assert eoq == 224

    def test_compute_rop(self, engine):
        # D = 1000, days = 300 -> 3.333/day. Lead = 5 days -> 16.66. Safety = 10 -> 26.66 -> 27
        rop = engine.compute_reorder_point(1000, 5, 10).unwrap()
        assert rop == 27
        
    def test_generate_procurement_target(self, engine):
        target = engine.generate_procurement_target(1000, 50.0, 10.0, 5, 10).unwrap()
        assert target["economic_order_quantity"] == 224
        assert target["reorder_point"] == 27
        assert target["annual_demand"] == 1000
        assert target["safety_stock"] == 10

    def test_invalid_demand(self, engine):
        assert engine.compute_eoq(-10, 50.0, 10.0).is_ok() is False

    def test_zero_unit_cost(self, engine):
        assert engine.compute_eoq(1000, 50.0, 0.0).is_ok() is False


# --- OmniPromptTokenBudgetEngine Tests ---
class TestPromptTokenBudget:
    @pytest.fixture
    def engine(self):
        return OmniPromptTokenBudgetEngine(max_context_window=1000, reserve_system=100, reserve_completion=100)

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()
        assert diag["max_window"] == 1000

    def test_allocate_proportional(self, engine):
        # Available: 800
        # Weights: 1.0, 1.0
        docs = [
            {"id": "doc1", "token_count": 500, "weight": 1.0},
            {"id": "doc2", "token_count": 500, "weight": 1.0}
        ]
        allocs = engine.allocate_tokens(docs).unwrap()
        assert allocs["doc1"] == 400
        assert allocs["doc2"] == 400

    def test_allocate_surplus_redistribution(self, engine):
        # Available: 800
        # doc1 wants 100, given weight 1.0 (target 400) -> uses 100, surplus 300
        # doc2 wants 700, given weight 1.0 (target 400) -> gets 400 + 300 surplus = 700
        docs = [
            {"id": "doc1", "token_count": 100, "weight": 1.0},
            {"id": "doc2", "token_count": 700, "weight": 1.0}
        ]
        allocs = engine.allocate_tokens(docs).unwrap()
        assert allocs["doc1"] == 100
        assert allocs["doc2"] == 700

    def test_optimize_payload(self, engine):
        docs = [
            {"id": "doc1", "token_count": 800, "weight": 1.0},
            {"id": "doc2", "token_count": 800, "weight": 1.0}
        ]
        payload = engine.optimize_payload(docs).unwrap()
        assert payload["system_prompt_reserve"] == 100
        assert payload["completion_margin"] == 100
        assert payload["total_consumed"] == 1000

    def test_reserves_exceed_max(self):
        engine_bad = OmniPromptTokenBudgetEngine(100, 100, 100)
        assert engine_bad.allocate_tokens([{"id": "1", "token_count": 50}]).is_ok() is False

    def test_no_weight_fallback(self, engine):
        docs = [
            {"id": "doc1", "token_count": 500},
            {"id": "doc2", "token_count": 500}
        ]
        allocs = engine.allocate_tokens(docs).unwrap()
        assert allocs["doc1"] == 400
        assert allocs["doc2"] == 400


# --- OmniEscapeRoomStateEngine Tests ---
class TestEscapeRoomState:
    @pytest.fixture
    def engine(self):
        state_graph = {
            "cell": {
                "actions": {
                    "use_key_on_door": {
                        "requires": ["rusty_key"],
                        "consumes": ["rusty_key"],
                        "awards": ["hallway_map"],
                        "transitions_to": "hallway"
                    },
                    "look_window": {
                        "transitions_to": "cell"
                    }
                }
            },
            "hallway": {
                "actions": {}
            }
        }
        return OmniEscapeRoomStateEngine(state_graph)

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

    def test_valid_transition(self, engine):
        inv = ["rusty_key", "note"]
        res = engine.evaluate_transition("cell", "use_key_on_door", inv).unwrap()
        assert res["new_room"] == "hallway"
        assert "rusty_key" not in res["new_inventory"]
        assert "note" in res["new_inventory"]
        assert "hallway_map" in res["new_inventory"]

    def test_missing_requirement(self, engine):
        inv = ["note"] # missing rusty_key
        assert engine.evaluate_transition("cell", "use_key_on_door", inv).is_ok() is False

    def test_action_without_requires(self, engine):
        inv = ["note"]
        res = engine.evaluate_transition("cell", "look_window", inv).unwrap()
        assert res["new_room"] == "cell"
        assert res["new_inventory"] == ["note"] # Unchanged

    def test_invalid_room(self, engine):
        assert engine.evaluate_transition("nowhere", "look", []).is_ok() is False

    def test_invalid_action(self, engine):
        assert engine.evaluate_transition("cell", "dance", []).is_ok() is False
