import pytest
from src.compute.python_core.omni_market_making_spread_engine import OmniMarketMakingSpreadEngine
from src.compute.python_core.omni_lsm_tree_compaction_engine import OmniLSMTreeCompactionEngine
from src.compute.python_core.omni_cellular_automata_engine import OmniCellularAutomataEngine
from src.compute.python_core.omni_hyperloglog_cardinality_engine import OmniHyperLogLogCardinalityEngine
from src.compute.python_core.omni_token_bucket_ratelimit_engine import OmniTokenBucketRateLimitEngine

# --- OmniMarketMakingSpreadEngine Tests ---
class TestMarketMakingSpread:
    @pytest.fixture
    def engine(self):
        return OmniMarketMakingSpreadEngine(target_inventory=0, risk_aversion_gamma=0.1)

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

    def test_reservation_price_flat(self, engine):
        # target=0, current=0 -> q=0. R = mid_price
        r_price = engine.compute_reservation_price(100.0, 0, 1.5, 1.0).unwrap()
        assert r_price == 100.0

    def test_reservation_price_long(self, engine):
        # target=0, current=10 -> q=10. R = 100 - (10 * 0.1 * 1.5^2 * 1) = 100 - (1 * 2.25) = 97.75
        r_price = engine.compute_reservation_price(100.0, 10, 1.5, 1.0).unwrap()
        assert r_price == 97.75

    def test_reservation_price_short(self, engine):
        # current=-10 -> q=-10. R = 100 - (-10 * 0.1 * 2.25) = 102.25
        r_price = engine.compute_reservation_price(100.0, -10, 1.5, 1.0).unwrap()
        assert r_price == 102.25

    def test_quotes(self, engine):
        quotes = engine.compute_quotes(100.0, 10, 1.5, 1.0, 0.5).unwrap()
        assert quotes["mid_price"] == 100.0
        assert quotes["reservation_price"] == 97.75
        assert quotes["bid"] < quotes["reservation_price"]
        assert quotes["ask"] > quotes["reservation_price"]
        assert quotes["spread"] > 0

    def test_invalid_mid_price(self, engine):
        assert not engine.compute_reservation_price(-10.0, 0, 1.5, 1.0).is_ok()

    def test_invalid_volatility(self, engine):
        assert not engine.compute_reservation_price(100.0, 0, -1.0, 1.0).is_ok()


# --- OmniLSMTreeCompactionEngine Tests ---
class TestLSMTreeCompaction:
    @pytest.fixture
    def engine(self):
        return OmniLSMTreeCompactionEngine(size_ratio=10.0, max_levels=4, base_level_mb=10.0)

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

    def test_compute_level_capacities(self, engine):
        caps = engine.compute_level_capacities().unwrap()
        assert caps[0] == 10.0
        assert caps[1] == 100.0
        assert caps[2] == 1000.0
        assert caps[3] == 10000.0

    def test_evaluate_tier_health_healthy(self, engine):
        # L0: 5MB, L1: 80MB, L2: 500MB (all below limits)
        sizes = {0: 5.0, 1: 80.0, 2: 500.0}
        health = engine.evaluate_tier_health(sizes).unwrap()
        assert health["healthy"] is True
        assert health["compactions_required"] == 0

    def test_evaluate_tier_health_unhealthy(self, engine):
        # L0 over limit, L1 over limit
        sizes = {0: 15.0, 1: 150.0, 2: 50.0}
        health = engine.evaluate_tier_health(sizes).unwrap()
        assert health["healthy"] is False
        assert health["compactions_required"] == 2
        assert health["queue"][0]["level"] == 0
        assert health["queue"][1]["level"] == 1
        # L0 targets L1
        assert health["queue"][0]["target_level"] == 1

    def test_invalid_parameters(self):
        engine2 = OmniLSMTreeCompactionEngine(0.5, 4, 10.0)
        assert not engine2.compute_level_capacities().is_ok()


# --- OmniCellularAutomataEngine Tests ---
class TestCellularAutomata:
    @pytest.fixture
    def engine(self):
        # Standard Conway's Game of Life
        return OmniCellularAutomataEngine(rule_survive=[2, 3], rule_born=[3], grid_dimensions=(3, 3))

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()
        assert diag["rule"] == "B3/S23"

    def test_compute_next_generation_block(self, engine):
        # Stable 2x2 block in top-left
        grid = [
            [1, 1, 0],
            [1, 1, 0],
            [0, 0, 0]
        ]
        next_gen = engine.compute_next_generation(grid).unwrap()
        assert next_gen == grid # Block is static

    def test_compute_next_generation_blinker(self, engine):
        # Horizontal blinker
        grid = [
            [0, 0, 0],
            [1, 1, 1],
            [0, 0, 0]
        ]
        next_gen = engine.compute_next_generation(grid).unwrap()
        # Should become vertical blinker
        assert next_gen[0][1] == 1
        assert next_gen[1][1] == 1
        assert next_gen[2][1] == 1
        
    def test_invalid_grid_dimensions(self, engine):
        bad_grid = [
            [0, 0],
            [0, 0]
        ]
        assert not engine.compute_next_generation(bad_grid).is_ok()


# --- OmniHyperLogLogCardinalityEngine Tests ---
class TestHyperLogLog:
    @pytest.fixture
    def engine(self):
        return OmniHyperLogLogCardinalityEngine(bucket_bits=4) # m=16 for speed

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()
        assert diag["buckets_m"] == 16

    def test_estimate_cardinality(self, engine):
        # Stream of 5 identical items + 5 distinct
        stream = [1, 1, 1, 1, 1, 2, 3, 4, 5, 6]
        res = engine.estimate_cardinality(stream).unwrap()
        assert "estimated_cardinality" in res
        assert res["exact_cardinality_count"] == 6

    def test_invalid_stream(self, engine):
        assert not engine.estimate_cardinality("not a list").is_ok()
        assert not engine.estimate_cardinality([1, "2"]).is_ok()


# --- OmniTokenBucketRateLimitEngine Tests ---
class TestTokenBucketRateLimit:
    @pytest.fixture
    def engine(self):
        return OmniTokenBucketRateLimitEngine(capacity=10.0, fill_rate_per_sec=2.0)

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()
        assert diag["capacity"] == 10.0

    def test_allowance_granted(self, engine):
        # Current: 5.0, Time delta: 1.0s (fills 2.0 -> 7.0). Request 3.0 -> Granted, leaves 4.0
        res = engine.compute_request_allowance(5.0, 100.0, 101.0, 3.0).unwrap()
        assert res["granted"] is True
        assert res["new_token_balance"] == 4.0

    def test_allowance_rejected(self, engine):
        # Current: 1.0, Time delta: 0.5s (fills 1.0 -> 2.0). Request 3.0 -> Rejected, leaves 2.0
        res = engine.compute_request_allowance(1.0, 100.0, 100.5, 3.0).unwrap()
        assert res["granted"] is False
        assert res["new_token_balance"] == 2.0

    def test_wait_time(self, engine):
        # Current tokens: 2.0, requested: 6.0. Deficit: 4.0. Rate: 2.0/s -> 2.0 seconds wait
        wait = engine.calculate_wait_time(2.0, 6.0).unwrap()
        assert wait == 2.0
        
    def test_wait_time_immediate(self, engine):
        wait = engine.calculate_wait_time(5.0, 3.0).unwrap()
        assert wait == 0.0

    def test_wait_time_impossible(self, engine):
        # Requested > capacity
        wait = engine.calculate_wait_time(5.0, 15.0).unwrap()
        assert wait == float("inf")

    def test_invalid_time(self, engine):
        assert not engine.compute_request_allowance(5.0, 101.0, 100.0, 1.0).is_ok()
