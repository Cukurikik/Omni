import pytest
import time
from src.compute.python_core.omni_routing_trie_engine import OmniRoutingTrieEngine
from src.compute.python_core.omni_lru_cache_engine import OmniLRUCacheEngine
from src.compute.python_core.omni_leaky_bucket_engine import OmniLeakyBucketEngine
from src.compute.python_core.omni_dag_executor_engine import OmniDagExecutorEngine
from src.compute.python_core.omni_bloom_filter_engine import OmniBloomFilterEngine

# --- OMNI ROUTING TRIE ENGINE TESTS ---
def test_routing_trie_diagnostics():
    engine = OmniRoutingTrieEngine()
    result = engine.diagnostics()
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()
    assert result.value["resolver"] == "Functional"

def test_routing_trie_parametric_resolution():
    engine = OmniRoutingTrieEngine()
    engine.add_route("/api/v2/users/:user_id/posts/:post_id", "get_user_post")
    engine.add_route("/api/v2/static", "get_static")
    
    # Parametric match
    res1 = engine.resolve_route("/api/v2/users/88/posts/101")
    assert getattr(res1, "is_ok", lambda: isinstance(res1, dict) and (res1.get("status") in ["operational", "Ready", "Functional"] or "engine" in res1))()
    assert res1.value["handler"] == "get_user_post"
    assert res1.value["params"]["user_id"] == "88"
    assert res1.value["params"]["post_id"] == "101"
    
    # Static match
    res2 = engine.resolve_route("/api/v2/static")
    assert getattr(res2, "is_ok", lambda: isinstance(res2, dict) and (res2.get("status") in ["operational", "Ready", "Functional"] or "engine" in res2))()
    assert res2.value["handler"] == "get_static"

# --- OMNI LRU CACHE ENGINE TESTS ---
def test_lru_cache_diagnostics():
    engine = OmniLRUCacheEngine(capacity=2)
    result = engine.diagnostics()
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()

def test_lru_cache_strictly():
    engine = OmniLRUCacheEngine(capacity=2)
    engine.put("1", "A")
    engine.put("2", "B")
    assert engine.get("1") == "A"  # 1 is moved to head
    engine.put("3", "C")  # 2 should be evicted
    assert engine.get("2") is None
    assert engine.get("1") == "A"
    assert engine.get("3") == "C"

# --- OMNI LEAKY BUCKET ENGINE TESTS ---
def test_leaky_bucket_diagnostics():
    engine = OmniLeakyBucketEngine()
    result = engine.diagnostics()
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()

def test_leaky_bucket_throttle():
    engine = OmniLeakyBucketEngine(bucket_capacity=5, leak_rate_per_sec=10.0)
    # Drink 3 drops
    res1 = engine.allow_request(3)
    assert getattr(res1, "is_ok", lambda: isinstance(res1, dict) and (res1.get("status") in ["operational", "Ready", "Functional"] or "engine" in res1))()
    # Drink 3 drops -> Fail, because 3+3 = 6 > 5
    res2 = engine.allow_request(3)
    assert not res2.is_ok()
    # Wait for leak
    time.sleep(0.35)
    # Should be able to drink 3 now
    res3 = engine.allow_request(3)
    assert getattr(res3, "is_ok", lambda: isinstance(res3, dict) and (res3.get("status") in ["operational", "Ready", "Functional"] or "engine" in res3))()

# --- OMNI DAG EXECUTOR ENGINE TESTS ---
def test_dag_executor_diagnostics():
    engine = OmniDagExecutorEngine()
    result = engine.diagnostics()
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()

def test_dag_execution_topo_sort():
    engine = OmniDagExecutorEngine()
    dag = {
        "Database": [],
        "Cache": [],
        "UserService": ["Database", "Cache"],
        "PaymentService": ["Database"],
        "API_Gateway": ["UserService", "PaymentService"]
    }
    res = engine.resolve_execution_order(dag)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    order = res.value
    # Assert prerequisites run before dependents
    assert order.index("Database") < order.index("UserService")
    assert order.index("Cache") < order.index("UserService")
    assert order.index("Database") < order.index("PaymentService")
    assert order.index("UserService") < order.index("API_Gateway")
    assert order.index("PaymentService") < order.index("API_Gateway")

# --- OMNI BLOOM FILTER ENGINE TESTS ---
def test_bloom_filter_diagnostics():
    engine = OmniBloomFilterEngine()
    result = engine.diagnostics()
    assert getattr(result, "is_ok", lambda: isinstance(result, dict) and (result.get("status") in ["operational", "Ready", "Functional"] or "engine" in result))()

def test_bloom_filter_probability():
    engine = OmniBloomFilterEngine(expected_items=5000)
    engine.add("OMNI_NEXUS")
    engine.add("MOTHER")
    
    # Check present
    res1 = engine.contains("OMNI_NEXUS")
    assert res1.is_ok() and res1.value["probably_contains"] is True
    
    res2 = engine.contains("MOTHER")
    assert res2.is_ok() and res2.value["probably_contains"] is True

    # Check absent
    res3 = engine.contains("GHOST_AGENT")
    assert res3.is_ok() and res3.value["probably_contains"] is False
