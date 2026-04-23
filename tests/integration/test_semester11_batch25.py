"""Integration tests for Semester 11 Batch 25 — 50 tests for 10 engines."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.compute.python_core.omni_decision_tree_classifier_engine import OmniDecisionTreeClassifierEngine
from src.compute.python_core.omni_crc_checksum_engine import OmniCrcChecksumEngine
from src.compute.python_core.omni_interval_scheduling_engine import OmniIntervalSchedulingEngine
from src.compute.python_core.omni_run_length_encoding_engine import OmniRunLengthEncodingEngine
from src.compute.python_core.omni_union_find_engine import OmniUnionFindEngine
from src.compute.python_core.omni_minimum_spanning_tree_engine import OmniMinimumSpanningTreeEngine
from src.compute.python_core.omni_bellman_ford_engine import OmniBellmanFordEngine
from src.compute.python_core.omni_sha256_hash_engine import OmniSha256HashEngine
from src.compute.python_core.omni_linear_regression_engine import OmniLinearRegressionEngine
from src.compute.python_core.omni_base64_engine import OmniBase64Engine

# ═══ Decision Tree ═══
def test_dt_fit():
    e = OmniDecisionTreeClassifierEngine()
    X = [[0,0],[0,1],[1,0],[1,1]]
    y = [0, 1, 1, 0]
    r = e.fit(X, y)
    assert r.is_ok() and r.value["trained"] is True

def test_dt_predict():
    e = OmniDecisionTreeClassifierEngine()
    X = [[0,0],[1,0],[0,1],[1,1]]
    y = [0, 1, 1, 1]
    e.fit(X, y)
    r = e.predict([[1,1]])
    assert r.is_ok() and r.value["predictions"][0] == 1

def test_dt_pure_class():
    e = OmniDecisionTreeClassifierEngine()
    X = [[i, i*2] for i in range(10)]
    y = [0]*10
    e.fit(X, y)
    r = e.predict([[5, 10]])
    assert r.is_ok() and r.value["predictions"][0] == 0

def test_dt_empty():
    e = OmniDecisionTreeClassifierEngine()
    r = e.fit([], [])
    assert not r.is_ok()

def test_dt_diagnostics():
    assert OmniDecisionTreeClassifierEngine().diagnostics()["status"] == "operational"

# ═══ CRC Checksum ═══
def test_crc32_basic():
    e = OmniCrcChecksumEngine()
    r = e.crc32(b"Hello, World!")
    assert r.is_ok() and isinstance(r.value["checksum"], int)

def test_crc32_empty():
    e = OmniCrcChecksumEngine()
    r = e.crc32(b"")
    assert r.is_ok() and r.value["checksum"] == 0

def test_adler32():
    e = OmniCrcChecksumEngine()
    r = e.adler32(b"Wikipedia")
    assert r.is_ok() and r.value["checksum"] == 300286872

def test_fletcher16():
    e = OmniCrcChecksumEngine()
    r = e.fletcher16(b"abcde")
    assert r.is_ok() and isinstance(r.value["checksum"], int)

def test_crc_verify():
    e = OmniCrcChecksumEngine()
    r1 = e.crc32(b"test data")
    r2 = e.verify(b"test data", r1.value["checksum"])
    assert r2.is_ok() and r2.value["match"] is True

def test_crc_diagnostics():
    assert OmniCrcChecksumEngine().diagnostics()["status"] == "operational"

# ═══ Interval Scheduling ═══
def test_interval_maximize():
    e = OmniIntervalSchedulingEngine()
    r = e.maximize_non_overlapping([(1,3),(2,5),(4,6),(6,8)])
    assert r.is_ok() and r.value["count"] == 3

def test_interval_merge():
    e = OmniIntervalSchedulingEngine()
    r = e.merge_overlapping([(1,3),(2,6),(8,10),(15,18)])
    assert r.is_ok() and r.value["count"] == 3

def test_interval_conflicts():
    e = OmniIntervalSchedulingEngine()
    r = e.find_conflicts([(1,5),(2,6),(7,9)])
    assert r.is_ok() and r.value["conflict_count"] == 1

def test_interval_diagnostics():
    assert OmniIntervalSchedulingEngine().diagnostics()["status"] == "operational"

# ═══ Run Length Encoding ═══
def test_rle_encode():
    e = OmniRunLengthEncodingEngine()
    r = e.encode("aaabbc")
    assert r.is_ok() and r.value["encoded"] == "a3b2c1"

def test_rle_decode():
    e = OmniRunLengthEncodingEngine()
    r = e.decode("a3b2c1")
    assert r.is_ok() and r.value["decoded"] == "aaabbc"

def test_rle_roundtrip():
    e = OmniRunLengthEncodingEngine()
    original = "xxxyyyzz"
    enc = e.encode(original)
    dec = e.decode(enc.value["encoded"])
    assert dec.value["decoded"] == original

def test_rle_single_chars():
    e = OmniRunLengthEncodingEngine()
    r = e.encode("abc")
    assert r.is_ok() and r.value["num_runs"] == 3

def test_rle_diagnostics():
    assert OmniRunLengthEncodingEngine().diagnostics()["status"] == "operational"

# ═══ Union Find ═══
def test_uf_basic():
    uf = OmniUnionFindEngine(5)
    r = uf.union(0, 1)
    assert r.is_ok() and r.value["merged"] is True

def test_uf_connected():
    uf = OmniUnionFindEngine(5)
    uf.union(0, 1)
    uf.union(1, 2)
    r = uf.connected(0, 2)
    assert r.is_ok() and r.value["connected"] is True

def test_uf_disconnected():
    uf = OmniUnionFindEngine(5)
    uf.union(0, 1)
    r = uf.connected(0, 3)
    assert r.is_ok() and r.value["connected"] is False

def test_uf_components():
    uf = OmniUnionFindEngine(4)
    uf.union(0, 1)
    uf.union(2, 3)
    r = uf.get_components()
    assert r.is_ok() and r.value["count"] == 2

def test_uf_diagnostics():
    assert OmniUnionFindEngine(1).diagnostics()["status"] == "operational"

# ═══ MST ═══
def test_mst_basic():
    e = OmniMinimumSpanningTreeEngine()
    r = e.kruskal(["A","B","C"], [("A","B",1),("B","C",2),("A","C",3)])
    assert r.is_ok() and r.value["total_weight"] == 3 and r.value["is_spanning"] is True

def test_mst_single():
    e = OmniMinimumSpanningTreeEngine()
    r = e.kruskal(["A"], [])
    assert r.is_ok() and r.value["total_weight"] == 0

def test_mst_diagnostics():
    assert OmniMinimumSpanningTreeEngine().diagnostics()["status"] == "operational"

# ═══ Bellman-Ford ═══
def test_bf_basic():
    e = OmniBellmanFordEngine()
    r = e.compute(["A","B","C"], [("A","B",1),("B","C",2),("A","C",4)], "A")
    assert r.is_ok() and r.value["distances"]["C"] == 3

def test_bf_negative():
    e = OmniBellmanFordEngine()
    r = e.compute(["A","B","C"], [("A","B",1),("B","C",-1),("A","C",5)], "A")
    assert r.is_ok() and r.value["distances"]["C"] == 0

def test_bf_diagnostics():
    assert OmniBellmanFordEngine().diagnostics()["status"] == "operational"

# ═══ SHA-256 ═══
def test_sha256_empty():
    e = OmniSha256HashEngine()
    r = e.hash(b"")
    assert r.is_ok() and r.value["hash"] == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

def test_sha256_hello():
    e = OmniSha256HashEngine()
    r = e.hash(b"hello")
    assert r.is_ok() and r.value["length"] == 64

def test_sha256_diagnostics():
    assert OmniSha256HashEngine().diagnostics()["status"] == "operational"

# ═══ Linear Regression ═══
def test_lr_fit():
    e = OmniLinearRegressionEngine()
    X = [[i] for i in range(10)]
    y = [2*i + 1 for i in range(10)]
    r = e.fit(X, y)
    assert r.is_ok() and r.value["r_squared"] > 0.99

def test_lr_predict():
    e = OmniLinearRegressionEngine()
    X = [[i] for i in range(10)]
    y = [3*i + 5 for i in range(10)]
    e.fit(X, y)
    r = e.predict([[10]])
    assert r.is_ok() and abs(r.value["predictions"][0] - 35) < 0.01

def test_lr_untrained():
    e = OmniLinearRegressionEngine()
    r = e.predict([[1]])
    assert not r.is_ok()

def test_lr_diagnostics():
    assert OmniLinearRegressionEngine().diagnostics()["status"] == "operational"

# ═══ Base64 ═══
def test_b64_encode():
    e = OmniBase64Engine()
    r = e.encode(b"Hello")
    assert r.is_ok() and r.value["encoded"] == "SGVsbG8="

def test_b64_decode():
    e = OmniBase64Engine()
    r = e.decode("SGVsbG8=")
    assert r.is_ok() and r.value["decoded"] == b"Hello"

def test_b64_roundtrip():
    e = OmniBase64Engine()
    data = b"The quick brown fox"
    enc = e.encode(data)
    dec = e.decode(enc.value["encoded"])
    assert dec.value["decoded"] == data

def test_b64_diagnostics():
    assert OmniBase64Engine().diagnostics()["status"] == "operational"

# ═══ Additional Coverage ═══
def test_mst_four_nodes():
    e = OmniMinimumSpanningTreeEngine()
    r = e.kruskal(["A","B","C","D"], [("A","B",1),("B","C",4),("A","C",3),("C","D",2),("B","D",5)])
    assert r.is_ok() and r.value["edge_count"] == 3

def test_uf_self_union():
    uf = OmniUnionFindEngine(3)
    r = uf.union(0, 0)
    assert r.is_ok() and r.value["merged"] is False

def test_bf_source_invalid():
    e = OmniBellmanFordEngine()
    r = e.compute(["A","B"], [("A","B",1)], "Z")
    assert not r.is_ok()

def test_interval_merge_empty():
    e = OmniIntervalSchedulingEngine()
    r = e.merge_overlapping([])
    assert r.is_ok() and r.value["count"] == 0

def test_b64_url_safe():
    e = OmniBase64Engine()
    r = e.encode(b"\xff\xfe\xfd", url_safe=True)
    assert r.is_ok() and "+" not in r.value["encoded"] and "/" not in r.value["encoded"]

def test_crc32_deterministic():
    e = OmniCrcChecksumEngine()
    r1 = e.crc32(b"consistent")
    r2 = e.crc32(b"consistent")
    assert r1.value["checksum"] == r2.value["checksum"]

def test_rle_long_run():
    e = OmniRunLengthEncodingEngine()
    r = e.encode("a" * 100)
    assert r.is_ok() and r.value["num_runs"] == 1

# ═══ Smoke ═══
def test_batch25_smoke():
    engines = [OmniDecisionTreeClassifierEngine(), OmniCrcChecksumEngine(), OmniIntervalSchedulingEngine(),
               OmniRunLengthEncodingEngine(), OmniUnionFindEngine(1), OmniMinimumSpanningTreeEngine(),
               OmniBellmanFordEngine(), OmniSha256HashEngine(), OmniLinearRegressionEngine(), OmniBase64Engine()]
    for eng in engines:
        assert eng.diagnostics()["status"] == "operational"
