import pytest
from src.compute.python_core.omni_consistent_hashing_ring_engine import OmniConsistentHashingRingEngine
from src.compute.python_core.omni_merkle_tree_integrity_engine import OmniMerkleTreeIntegrityEngine
from src.compute.python_core.omni_pid_controller_feedback_engine import OmniPIDControllerFeedbackEngine
from src.compute.python_core.omni_simulated_annealing_optimizer_engine import OmniSimulatedAnnealingOptimizerEngine
from src.compute.python_core.omni_huffman_coding_compression_engine import OmniHuffmanCodingCompressionEngine

# --- OmniConsistentHashingRingEngine Tests ---
class TestConsistentHashingRing:
    @pytest.fixture
    def engine(self):
        return OmniConsistentHashingRingEngine(virtual_nodes=100)

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()
        assert diag["virtual_nodes"] == 100

    def test_add_and_locate_node(self, engine):
        engine.add_node("node-A").unwrap()
        engine.add_node("node-B").unwrap()
        engine.add_node("node-C").unwrap()
        
        owner = engine.locate_node("user_123").unwrap()
        assert owner in ("node-A", "node-B", "node-C")

    def test_add_duplicate(self, engine):
        assert engine.add_node("node-A").unwrap() is True
        assert engine.add_node("node-A").unwrap() is False

    def test_remove_node(self, engine):
        engine.add_node("node-A").unwrap()
        assert engine.remove_node("node-A").unwrap() is True
        assert engine.remove_node("node-A").unwrap() is False

    def test_locate_empty_ring(self, engine):
        assert not engine.locate_node("data").is_ok()


# --- OmniMerkleTreeIntegrityEngine Tests ---
class TestMerkleTreeIntegrity:
    @pytest.fixture
    def engine(self):
        return OmniMerkleTreeIntegrityEngine(raw_blocks=["A", "B", "C", "D", "E"])

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()
        assert diag["block_count"] == 5

    def test_build_tree(self, engine):
        root = engine.build_tree().unwrap()
        assert isinstance(root, str)
        assert len(root) == 64 # SHA256 length

    def test_proof_verification(self, engine):
        root = engine.build_tree().unwrap()
        # Create proof for block "C" (index 2)
        proof = engine.generate_proof(2).unwrap()
        
        valid = OmniMerkleTreeIntegrityEngine.verify_proof("C", proof, root)
        assert valid is True
        
        invalid = OmniMerkleTreeIntegrityEngine.verify_proof("X", proof, root)
        assert invalid is False

    def test_proof_without_tree(self, engine):
        assert not engine.generate_proof(0).is_ok()

    def test_invalid_index(self, engine):
        engine.build_tree().unwrap()
        assert not engine.generate_proof(10).is_ok()


# --- OmniPIDControllerFeedbackEngine Tests ---
class TestPIDControllerFeedback:
    @pytest.fixture
    def engine(self):
        return OmniPIDControllerFeedbackEngine(kp=0.5, ki=0.1, kd=0.05, setpoint=100.0)

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()
        assert diag["setpoint"] == 100.0

    def test_compute_correction(self, engine):
        # Current = 80, Setpoint = 100 => Error = 20
        res = engine.compute_correction(80.0, 1.0).unwrap()
        assert res["error"] == 20.0
        # P = 0.5 * 20 = 10.0
        assert res["p_out"] == 10.0
        # I = 0.1 * (20 * 1) = 2.0
        assert res["i_out"] == 2.0
        # D = 0.05 * ((20 - 0) / 1) = 1.0
        assert res["d_out"] == 1.0
        assert res["correction"] == 13.0

    def test_reset_state(self, engine):
        engine.compute_correction(80.0, 1.0).unwrap()
        assert engine.integral > 0
        engine.reset_state().unwrap()
        assert engine.integral == 0.0
        assert engine.previous_error == 0.0

    def test_invalid_dt(self, engine):
        assert not engine.compute_correction(80.0, -1.0).is_ok()


# --- OmniSimulatedAnnealingOptimizerEngine Tests ---
class TestSimulatedAnnealingOptimizer:
    @pytest.fixture
    def engine(self):
        return OmniSimulatedAnnealingOptimizerEngine(initial_temperature=1000.0, cooling_rate=0.9)

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()

    def test_compute_temperature(self, engine):
        temp = engine.compute_temperature(2).unwrap()
        # 1000 * (0.9^2) = 810
        assert temp == 810.0

    def test_evaluate_transition_better(self, engine):
        res = engine.evaluate_transition(current_cost=50.0, new_cost=40.0, epoch=5).unwrap()
        assert res["accepted_transition"] is True
        assert res["acceptance_probability"] == 1.0

    def test_evaluate_transition_worse(self, engine):
        res = engine.evaluate_transition(current_cost=50.0, new_cost=55.0, epoch=1).unwrap()
        # temp = 900. delta = 5. prob = e^(-5/900) ~ 0.99
        assert "accepted_transition" in res

    def test_evaluate_transition_frozen(self, engine):
        # Epoch 200 implies temp practically 0
        res = engine.evaluate_transition(current_cost=50.0, new_cost=55.0, epoch=200).unwrap()
        assert res["accepted_transition"] is False
        assert res["acceptance_probability"] == 0.0

    def test_invalid_epoch(self, engine):
        assert not engine.compute_temperature(-1).is_ok()


# --- OmniHuffmanCodingCompressionEngine Tests ---
class TestHuffmanCodingCompression:
    @pytest.fixture
    def engine(self):
        return OmniHuffmanCodingCompressionEngine()

    def test_diagnostics(self, engine):
        diag = engine.diagnostics()
        assert getattr(diag, "is_ok", lambda: isinstance(diag, dict) and (diag.get("status") in ["operational", "Ready", "Functional"] or "engine" in diag))()
        assert diag["is_compiled"] is False

    def test_compile_and_encode_decode(self, engine):
        payload = "OMNI_FRAMEWORK_SEMESTER_10"
        
        res = engine.compile_encoding_tree(payload).unwrap()
        assert res["unique_characters"] > 0
        assert res["efficiency_saving_ratio"] > 0.0
        
        encoded = engine.encode(payload).unwrap()
        assert set(encoded).issubset({"0", "1"})
        
        decoded = engine.decode(encoded).unwrap()
        assert decoded == payload

    def test_encode_uncompiled(self, engine):
        assert not engine.encode("TEST").is_ok()

    def test_encode_unknown_char(self, engine):
        engine.compile_encoding_tree("ABC").unwrap()
        assert not engine.encode("X").is_ok()

    def test_decode_invalid_binary(self, engine):
        engine.compile_encoding_tree("ABC").unwrap()
        assert not engine.decode("2").is_ok()
