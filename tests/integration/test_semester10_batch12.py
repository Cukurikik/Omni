import pytest
from src.compute.python_core.omni_ts_node_emission_engine import OmniTsNodeEmissionEngine
from src.compute.python_core.omni_memory_eviction_algorithm_engine import OmniMemoryEvictionAlgorithmEngine
from src.compute.python_core.omni_weighted_routing_algorithm_engine import OmniWeightedRoutingAlgorithmEngine
from src.compute.python_core.omni_fair_scheduling_algorithm_engine import OmniFairSchedulingAlgorithmEngine
from src.compute.python_core.omni_wal_checkpoint_algorithm_engine import OmniWalCheckpointAlgorithmEngine

# --- TS EMISSION TESTS ---
def test_ts_diagnostics():
    engine = OmniTsNodeEmissionEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_ts_emit_var():
    engine = OmniTsNodeEmissionEngine()
    ast = {"kind": "VariableDeclaration", "name": "myString", "type": "string"}
    res = engine.emit_node(ast)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["emitted_string"] == "let myString: string = undefined;"

def test_ts_emit_invalid():
    engine = OmniTsNodeEmissionEngine()
    ast = {"kind": "UnknownNode"}
    res = engine.emit_node(ast)
    assert not res.is_ok()

# --- MEMORY EVICTION TESTS ---
def test_mem_diagnostics():
    engine = OmniMemoryEvictionAlgorithmEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_mem_lru_eject():
    engine = OmniMemoryEvictionAlgorithmEngine()
    state = {"A": 50, "B": 10, "C": 55}
    res = engine.calculate_lru_ejection(state, 60)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    # B is 50 ticks old, A is 10, C is 5.
    assert res.value["target_key"] == "B"

def test_mem_temporal_anomaly():
    engine = OmniMemoryEvictionAlgorithmEngine()
    state = {"A": 100}
    res = engine.calculate_lru_ejection(state, 50) # Ticks in future
    assert not res.is_ok()

# --- WEIGHTED ROUTING TESTS ---
def test_rout_diagnostics():
    engine = OmniWeightedRoutingAlgorithmEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_rout_weight_calc():
    engine = OmniWeightedRoutingAlgorithmEngine()
    nodes = [
        {"ip": "1.1.1.1", "weight": 10, "current_conn": 9},  # score 1
        {"ip": "2.2.2.2", "weight": 5, "current_conn": 0}    # score 5
    ]
    res = engine.select_optimal_node(nodes)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["selected_ip"] == "2.2.2.2"

def test_rout_down_nodes():
    engine = OmniWeightedRoutingAlgorithmEngine()
    nodes = [{"ip": "1.1.1.1", "weight": 0, "current_conn": 0}]
    res = engine.select_optimal_node(nodes)
    assert not res.is_ok()

# --- FAIR SCHEDULING TESTS ---
def test_fair_diagnostics():
    engine = OmniFairSchedulingAlgorithmEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_fair_vruntime():
    engine = OmniFairSchedulingAlgorithmEngine()
    qs = [{"pid": 1, "vruntime": 9999}, {"pid": 2, "vruntime": 10}]
    res = engine.select_next_process(qs)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["selected_pid"] == 2

def test_fair_malformed():
    engine = OmniFairSchedulingAlgorithmEngine()
    qs = [{"process_id": 1}]
    res = engine.select_next_process(qs)
    assert not res.is_ok()

# --- WAL CHECKPOINT TESTS ---
def test_wal_diagnostics():
    engine = OmniWalCheckpointAlgorithmEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_wal_volume_trigger():
    engine = OmniWalCheckpointAlgorithmEngine()
    res = engine.evaluate_checkpoint_necessity(wal_bytes_written=1_500_000_000, time_since_last_sec=10)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["trigger_action"] == "CHECKPOINT"
    assert res.value["reason"] == "VOLUME_EXCEEDED"

def test_wal_timeout_trigger():
    engine = OmniWalCheckpointAlgorithmEngine()
    res = engine.evaluate_checkpoint_necessity(wal_bytes_written=1000, time_since_last_sec=350)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["trigger_action"] == "CHECKPOINT"
    assert res.value["reason"] == "TIMEOUT_EXCEEDED"

def test_wal_negative():
    engine = OmniWalCheckpointAlgorithmEngine()
    res = engine.evaluate_checkpoint_necessity(-10, 100)
    assert not res.is_ok()
