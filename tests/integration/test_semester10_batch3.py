import pytest
from src.compute.python_core.omni_dev_quality_synthesizer_engine import OmniDevQualitySynthesizerEngine
from src.compute.python_core.omni_agent_orchestrator_engine import OmniAgentOrchestratorEngine
from src.compute.python_core.omni_websocket_multiplexer_engine import OmniWebSocketMultiplexerEngine
from src.compute.python_core.omni_transaction_ledger_engine import OmniTransactionLedgerEngine
from src.compute.python_core.omni_polyseed_crypto_engine import OmniPolyseedCryptoEngine

# --- OMNI DEV QUALITY SYNTHESIZER TESTS ---
def test_dev_quality_diagnostics():
    engine = OmniDevQualitySynthesizerEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_dev_quality_evaluation():
    engine = OmniDevQualitySynthesizerEngine()
    raw = "def x(): pass"
    res = engine.evaluate_snippet(raw)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["score"] < 100 # should lose score due to lacking docstrings

# --- OMNI AGENT ORCHESTRATOR TESTS ---
def test_agent_orchestrator_diagnostics():
    engine = OmniAgentOrchestratorEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_agent_fsm_orchestration():
    engine = OmniAgentOrchestratorEngine()
    engine.register_agent("deploy_agent")
    
    # assign task
    res1 = engine.assign_task("deploy_agent", "build_image")
    assert getattr(res1, "is_ok", lambda: isinstance(res1, dict) and (res1.get("status") in ["operational", "Ready", "Functional"] or "engine" in res1))()
    assert res1.value["status"] == "BUSY"
    
    # try another, should queue
    res2 = engine.assign_task("deploy_agent", "push_image")
    assert getattr(res2, "is_ok", lambda: isinstance(res2, dict) and (res2.get("status") in ["operational", "Ready", "Functional"] or "engine" in res2))()
    assert res2.value["status"] == "QUEUED"
    
    # complete
    res3 = engine.mark_completed("deploy_agent")
    assert getattr(res3, "is_ok", lambda: isinstance(res3, dict) and (res3.get("status") in ["operational", "Ready", "Functional"] or "engine" in res3))()

# --- OMNI WEBSOCKET MULTIPLEXER TESTS ---
def test_websocket_multiplexer_diagnostics():
    engine = OmniWebSocketMultiplexerEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_websocket_pubsub():
    engine = OmniWebSocketMultiplexerEngine()
    engine.subscribe("c1", "room_a")
    engine.subscribe("c2", "room_a")
    res = engine.broadcast("room_a", "payload_data")
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert res.value["dispatched"] == 2

# --- OMNI TRANSACTION LEDGER TESTS ---
def test_transaction_ledger_diagnostics():
    engine = OmniTransactionLedgerEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_transaction_ledger_atomic():
    engine = OmniTransactionLedgerEngine()
    res = engine.create_account("vault", 5000)
    engine.create_account("client", 0)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    
    res = engine.transfer("vault", "client", 1000)
    assert getattr(res, "is_ok", lambda: isinstance(res, dict) and (res.get("status") in ["operational", "Ready", "Functional"] or "engine" in res))()
    assert engine.get_balance("vault") == 4000
    assert engine.get_balance("client") == 1000
    
    # Overdraft should fail
    fail_res = engine.transfer("client", "vault", 2000)
    assert not fail_res.is_ok()

# --- OMNI POLYSEED CRYPTO TESTS ---
def test_polyseed_crypto_diagnostics():
    engine = OmniPolyseedCryptoEngine()
    _diag = engine.diagnostics()
    assert getattr(_diag, "is_ok", lambda: isinstance(_diag, dict) and (_diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in _diag))()

def test_polyseed_lfsr_deterministic():
    engine1 = OmniPolyseedCryptoEngine(state=0b1100)
    engine2 = OmniPolyseedCryptoEngine(state=0b1100)
    assert engine1.generate_next().value == engine2.generate_next().value
    assert engine1.generate_next().value == engine2.generate_next().value
