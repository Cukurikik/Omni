"""Integration tests for Semester 11 Batch 26 — 50 tests for 10 engines."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.compute.python_core.omni_skip_list_engine import OmniSkipListEngine
from src.compute.python_core.omni_edit_distance_dp_engine import OmniEditDistanceDpEngine
from src.compute.python_core.omni_max_flow_engine import OmniMaxFlowEngine
from src.compute.python_core.omni_suffix_array_engine import OmniSuffixArrayEngine
from src.compute.python_core.omni_trie_engine import OmniTrieEngine
from src.compute.python_core.omni_longest_common_subsequence_engine import OmniLongestCommonSubsequenceEngine
from src.compute.python_core.omni_matrix_multiplication_engine import OmniMatrixMultiplicationEngine
from src.compute.python_core.omni_rate_limiter_engine import OmniRateLimiterEngine
from src.compute.python_core.omni_quicksort_engine import OmniQuicksortEngine

# ═══ Skip List ═══
def test_skip_insert():
    sl = OmniSkipListEngine()
    r = sl.insert(5, "five")
    assert r.is_ok() and r.value["inserted"] is True

def test_skip_search_found():
    sl = OmniSkipListEngine()
    sl.insert(10, "ten")
    r = sl.search(10)
    assert r.is_ok() and r.value["found"] is True

def test_skip_search_missing():
    sl = OmniSkipListEngine()
    sl.insert(1)
    r = sl.search(99)
    assert r.is_ok() and r.value["found"] is False

def test_skip_order():
    sl = OmniSkipListEngine()
    for k in [5,3,7,1,4]:
        sl.insert(k)
    r = sl.to_list()
    assert r.is_ok() and [i["key"] for i in r.value["items"]] == [1,3,4,5,7]

def test_skip_diagnostics():
    assert OmniSkipListEngine().diagnostics()["status"] == "operational"

# ═══ Edit Distance DP ═══
def test_ed_basic():
    e = OmniEditDistanceDpEngine()
    r = e.compute("kitten", "sitting")
    assert r.is_ok() and r.value["distance"] == 3

def test_ed_identical():
    e = OmniEditDistanceDpEngine()
    r = e.compute("abc", "abc")
    assert r.is_ok() and r.value["distance"] == 0

def test_ed_operations():
    e = OmniEditDistanceDpEngine()
    r = e.compute("abc", "axc")
    assert r.is_ok() and r.value["op_count"] == 1

def test_ed_damerau():
    e = OmniEditDistanceDpEngine()
    r = e.damerau("ab", "ba")
    assert r.is_ok() and r.value["distance"] == 1

def test_ed_diagnostics():
    assert OmniEditDistanceDpEngine().diagnostics()["status"] == "operational"

# ═══ Max Flow ═══
def test_maxflow_basic():
    e = OmniMaxFlowEngine()
    r = e.compute(["S","A","B","T"], [("S","A",10),("S","B",5),("A","T",8),("B","T",7),("A","B",3)], "S", "T")
    assert r.is_ok() and r.value["max_flow"] == 15

def test_maxflow_no_path():
    e = OmniMaxFlowEngine()
    r = e.compute(["S","T"], [], "S", "T")
    assert r.is_ok() and r.value["max_flow"] == 0

def test_maxflow_single_edge():
    e = OmniMaxFlowEngine()
    r = e.compute(["S","T"], [("S","T",42)], "S", "T")
    assert r.is_ok() and r.value["max_flow"] == 42

def test_maxflow_diagnostics():
    assert OmniMaxFlowEngine().diagnostics()["status"] == "operational"

# ═══ Suffix Array ═══
def test_sa_build():
    e = OmniSuffixArrayEngine()
    r = e.build("banana")
    assert r.is_ok() and r.value["suffix_array"] == [5, 3, 1, 0, 4, 2]

def test_sa_search():
    e = OmniSuffixArrayEngine()
    r = e.build("banana")
    sa = r.value["suffix_array"]
    r2 = e.search("banana", sa, "an")
    assert r2.is_ok() and r2.value["count"] == 2

def test_sa_search_missing():
    e = OmniSuffixArrayEngine()
    r = e.build("banana")
    r2 = e.search("banana", r.value["suffix_array"], "xyz")
    assert r2.is_ok() and r2.value["found"] is False

def test_sa_lcp():
    e = OmniSuffixArrayEngine()
    r = e.build("banana")
    r2 = e.build_lcp("banana", r.value["suffix_array"])
    assert r2.is_ok() and r2.value["length"] == 6

def test_sa_diagnostics():
    assert OmniSuffixArrayEngine().diagnostics()["status"] == "operational"

# ═══ Trie ═══
def test_trie_insert():
    t = OmniTrieEngine()
    r = t.insert("hello")
    assert r.is_ok() and r.value["inserted"] is True

def test_trie_search():
    t = OmniTrieEngine()
    t.insert("hello")
    r = t.search("hello")
    assert r.is_ok() and r.value["found"] is True

def test_trie_prefix():
    t = OmniTrieEngine()
    t.insert("hello"); t.insert("help")
    r = t.starts_with("hel")
    assert r.is_ok() and r.value["has_prefix"] is True and r.value["count"] == 2

def test_trie_autocomplete():
    t = OmniTrieEngine()
    for w in ["apple", "app", "application", "banana"]:
        t.insert(w)
    r = t.autocomplete("app")
    assert r.is_ok() and r.value["count"] == 3

def test_trie_diagnostics():
    assert OmniTrieEngine().diagnostics()["status"] == "operational"

# ═══ LCS ═══
def test_lcs_basic():
    e = OmniLongestCommonSubsequenceEngine()
    r = e.compute("ABCBDAB", "BDCAB")
    assert r.is_ok() and r.value["length"] == 4

def test_lcs_identical():
    e = OmniLongestCommonSubsequenceEngine()
    r = e.compute("abc", "abc")
    assert r.is_ok() and r.value["lcs"] == "abc"

def test_lcs_disjoint():
    e = OmniLongestCommonSubsequenceEngine()
    r = e.compute("abc", "xyz")
    assert r.is_ok() and r.value["length"] == 0

def test_lcs_diff():
    e = OmniLongestCommonSubsequenceEngine()
    r = e.diff("abc", "adc")
    assert r.is_ok() and len(r.value["diff"]) > 0

def test_lcs_diagnostics():
    assert OmniLongestCommonSubsequenceEngine().diagnostics()["status"] == "operational"

# ═══ Matrix Multiplication ═══
def test_mm_basic():
    e = OmniMatrixMultiplicationEngine()
    A = [[1,2],[3,4]]
    B = [[5,6],[7,8]]
    r = e.multiply(A, B)
    assert r.is_ok() and r.value["result"] == [[19,22],[43,50]]

def test_mm_identity():
    e = OmniMatrixMultiplicationEngine()
    r = e.identity(3)
    assert r.is_ok() and r.value["result"][1][1] == 1.0

def test_mm_determinant():
    e = OmniMatrixMultiplicationEngine()
    r = e.determinant([[1,2],[3,4]])
    assert r.is_ok() and r.value["determinant"] == -2.0

def test_mm_transpose():
    e = OmniMatrixMultiplicationEngine()
    r = e.transpose([[1,2,3],[4,5,6]])
    assert r.is_ok() and r.value["shape"] == [3, 2]

def test_mm_diagnostics():
    assert OmniMatrixMultiplicationEngine().diagnostics()["status"] == "operational"

# ═══ Rate Limiter ═══
def test_rl_create():
    e = OmniRateLimiterEngine()
    r = e.create_bucket("api", 10, 1.0)
    assert r.is_ok() and r.value["created"] is True

def test_rl_acquire():
    e = OmniRateLimiterEngine()
    e.create_bucket("api", 10, 100.0)
    r = e.acquire("api", 1)
    assert r.is_ok() and r.value["allowed"] is True

def test_rl_diagnostics():
    assert OmniRateLimiterEngine().diagnostics()["status"] == "operational"

# ═══ Quicksort ═══
def test_qs_basic():
    e = OmniQuicksortEngine()
    r = e.sort([5,3,8,1,9,2,7])
    assert r.is_ok() and r.value["sorted"] == [1,2,3,5,7,8,9]

def test_qs_reverse():
    e = OmniQuicksortEngine()
    r = e.sort([1,2,3], reverse=True)
    assert r.is_ok() and r.value["sorted"] == [3,2,1]

def test_qs_empty():
    e = OmniQuicksortEngine()
    r = e.sort([])
    assert r.is_ok() and r.value["sorted"] == []

def test_qs_diagnostics():
    assert OmniQuicksortEngine().diagnostics()["status"] == "operational"

# ═══ Additional Coverage ═══
def test_skip_update():
    sl = OmniSkipListEngine()
    sl.insert(5, "old")
    r = sl.insert(5, "new")
    assert r.is_ok() and r.value["updated"] is True

def test_ed_weighted():
    e = OmniEditDistanceDpEngine()
    r = e.compute("a", "b", insert_cost=2, delete_cost=2, sub_cost=3)
    assert r.is_ok() and r.value["distance"] == 3

def test_trie_duplicate():
    t = OmniTrieEngine()
    t.insert("test")
    r = t.insert("test")
    assert r.is_ok() and r.value["already_exists"] is True

def test_lcs_similarity():
    e = OmniLongestCommonSubsequenceEngine()
    r = e.compute("abcdef", "abcdef")
    assert r.is_ok() and r.value["similarity"] == 1.0

def test_mm_dim_mismatch():
    e = OmniMatrixMultiplicationEngine()
    r = e.multiply([[1,2,3]], [[1],[2]])
    assert not r.is_ok()

def test_rl_fixed_window():
    e = OmniRateLimiterEngine()
    r = e.fixed_window_check("user1", 5, 60.0, current_time=100.0)
    assert r.is_ok() and r.value["allowed"] is True

def test_qs_duplicates():
    e = OmniQuicksortEngine()
    r = e.sort([3,1,3,1,3])
    assert r.is_ok() and r.value["sorted"] == [1,1,3,3,3]

def test_sa_single_char():
    e = OmniSuffixArrayEngine()
    r = e.build("a")
    assert r.is_ok() and r.value["suffix_array"] == [0]

# ═══ Smoke ═══
def test_batch26_smoke():
    engines = [OmniSkipListEngine(), OmniEditDistanceDpEngine(), OmniMaxFlowEngine(),
               OmniSuffixArrayEngine(), OmniTrieEngine(), OmniLongestCommonSubsequenceEngine(),
               OmniMatrixMultiplicationEngine(), OmniRateLimiterEngine(), OmniQuicksortEngine()]
    for eng in engines:
        assert eng.diagnostics()["status"] == "operational"
