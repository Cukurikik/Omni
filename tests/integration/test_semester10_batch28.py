import pytest
from src.compute.python_core.omni_dijkstra_routing_engine import OmniDijkstraRoutingEngine
from src.compute.python_core.omni_crc_polynomial_hashing_engine import OmniCRCPolynomialHashingEngine
from src.compute.python_core.omni_bloom_filter_membership_engine import OmniBloomFilterMembershipEngine
from src.compute.python_core.omni_leaky_bucket_ratelimit_engine import OmniLeakyBucketRateLimitEngine
from src.compute.python_core.omni_exponential_backoff_jitter_engine import OmniExponentialBackoffJitterEngine

# --- OmniDijkstraRoutingEngine Tests ---
class TestDijkstraRouting:
    @pytest.fixture
    def engine(self):
        graph = {
            "A": {"B": 1.0, "C": 4.0},
            "B": {"A": 1.0, "C": 2.0, "D": 5.0},
            "C": {"A": 4.0, "B": 2.0, "D": 1.0},
            "D": {"B": 5.0, "C": 1.0}
        }
        return OmniDijkstraRoutingEngine(adjacency_list=graph)

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

    def test_compute_shortest_path(self, engine):
        # A -> B (1) -> C (2) -> D (1) = 4.0
        res = engine.compute_shortest_path("A", "D").unwrap()
        assert res["total_cost"] == 4.0
        assert res["path_vector"] == ["A", "B", "C", "D"]
        assert res["hops"] == 3

    def test_unreachable_target(self, engine):
        engine.graph["E"] = {} # stranded node
        assert not engine.compute_shortest_path("A", "E").is_ok()

    def test_invalid_start_node(self, engine):
        assert not engine.compute_shortest_path("X", "A").is_ok()

    def test_evaluate_reachability(self, engine):
        res = engine.evaluate_reachability("A").unwrap()
        assert res["A"] == 0.0
        assert res["B"] == 1.0
        assert res["C"] == 3.0
        assert res["D"] == 4.0


# --- OmniCRCPolynomialHashingEngine Tests ---
class TestCRCPolynomial:
    @pytest.fixture
    def engine(self):
        # Generic 8-bit CRC polynomial for speed (e.g. 0x07)
        return OmniCRCPolynomialHashingEngine(polynomial=0x07, width=8, initial_value=0x00, final_xor_value=0x00)

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

    def test_compute_crc(self, engine):
        # compute over some bytes
        data = b"OMNI"
        res = engine.compute_crc(data).unwrap()
        assert isinstance(res, int)

    def test_verify_integrity_true(self, engine):
        data = b"OMNI"
        crc = engine.compute_crc(data).unwrap()
        valid = engine.verify_integrity(data, crc).unwrap()
        assert valid is True

    def test_verify_integrity_false(self, engine):
        data = b"OMNI"
        data2 = b"OMNA"
        crc = engine.compute_crc(data).unwrap()
        valid = engine.verify_integrity(data2, crc).unwrap()
        assert valid is False

    def test_invalid_data(self, engine):
        assert not engine.compute_crc("not bytes").is_ok()


# --- OmniBloomFilterMembershipEngine Tests ---
class TestBloomFilter:
    @pytest.fixture
    def engine(self):
        return OmniBloomFilterMembershipEngine(expected_items=100, target_false_positive_rate=0.01)

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()
        assert diag["bit_array_size"] > 0
        assert diag["hash_count"] > 0

    def test_insert_and_contains(self, engine):
        engine.insert("omni-1").unwrap()
        engine.insert("omni-2").unwrap()
        
        assert engine.contains("omni-1").unwrap() is True
        assert engine.contains("omni-2").unwrap() is True
        assert engine.contains("omni-3").unwrap() is False # with very high probability

    def test_estimate_fp_rate(self, engine):
        for i in range(50):
            engine.insert(f"item-{i}").unwrap()
            
        fp_rate = engine.estimate_current_fp_rate().unwrap()
        assert 0.0 < fp_rate < 0.02 # Roughly within optimal bounds for 50 items

    def test_invalid_type(self, engine):
        assert not engine.insert(12345).is_ok()
        assert not engine.contains({"data": 1}).is_ok()


# --- OmniLeakyBucketRateLimitEngine Tests ---
class TestLeakyBucketRateLimit:
    @pytest.fixture
    def engine(self):
        return OmniLeakyBucketRateLimitEngine(capacity=10.0, leak_rate_per_sec=2.0)

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()
        assert diag["capacity"] == 10.0

    def test_compute_enqueue_accepted(self, engine):
        # Bucket has 5.0 water. 1 sec passes -> drains 2.0 -> returns to 3.0. Add 3.0 => 6.0
        res = engine.compute_enqueue(5.0, 100.0, 101.0, 3.0).unwrap()
        assert res["accepted"] is True
        assert res["new_water_level"] == 6.0
        assert res["dropped_volume"] == 0.0

    def test_compute_enqueue_rejected(self, engine):
        # Bucket has 9.0. 0.5s passes -> drains 1.0 -> 8.0. Add 5.0 => 13.0 (Capacity 10.0 => drops 5.0 entirely)
        res = engine.compute_enqueue(9.0, 100.0, 100.5, 5.0).unwrap()
        assert res["accepted"] is False
        assert res["new_water_level"] == 8.0
        assert res["dropped_volume"] == 5.0

    def test_extract_drain_time(self, engine):
        # 4.0 / 2.0 = 2.0 secs
        dt = engine.extract_drain_time(4.0).unwrap()
        assert dt == 2.0

    def test_invalid_time_sequence(self, engine):
        assert not engine.compute_enqueue(5.0, 100.0, 99.0, 1.0).is_ok()


# --- OmniExponentialBackoffJitterEngine Tests ---
class TestExponentialBackoffJitter:
    @pytest.fixture
    def engine(self):
        return OmniExponentialBackoffJitterEngine(base_delay_ms=100.0, max_delay_ms=5000.0, jitter_factor=0.5)

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()
        assert diag["jitter_factor"] == 0.5

    def test_compute_backoff_attempt_0(self, engine):
        # target exp = 100ms
        # jitter range = 50ms. min = 50, max = 100.
        res = engine.compute_backoff(0).unwrap()
        assert res["raw_exponential_ms"] == 100.0
        assert 50.0 <= res["jittered_delay_ms"] <= 100.0
        
    def test_compute_backoff_attempt_3(self, engine):
        # target exp = 800ms
        res = engine.compute_backoff(3).unwrap()
        assert res["raw_exponential_ms"] == 800.0
        assert 400.0 <= res["jittered_delay_ms"] <= 800.0

    def test_compute_backoff_max_cap(self, engine):
        # attempt 20 is huge
        res = engine.compute_backoff(20).unwrap()
        assert res["raw_exponential_ms"] == 5000.0
        assert 2500.0 <= res["jittered_delay_ms"] <= 5000.0
        
    def test_invalid_attempt(self, engine):
        assert not engine.compute_backoff(-1).is_ok()
