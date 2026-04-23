"""Integration tests for Semester 11 Batch 24 — 50 tests for 10 engines."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.compute.python_core.omni_prime_sieve_engine import OmniPrimeSieveEngine
from src.compute.python_core.omni_convolution_filter_engine import OmniConvolutionFilterEngine
from src.compute.python_core.omni_regex_parser_engine import OmniRegexParserEngine
from src.compute.python_core.omni_topological_sort_engine import OmniTopologicalSortEngine
from src.compute.python_core.omni_hyperloglog_engine import OmniHyperloglogEngine
from src.compute.python_core.omni_binary_search_tree_engine import OmniBinarySearchTreeEngine
from src.compute.python_core.omni_moving_average_engine import OmniMovingAverageEngine
from src.compute.python_core.omni_knapsack_dp_engine import OmniKnapsackDynamicProgrammingEngine
from src.compute.python_core.omni_levenshtein_distance_engine import OmniLevenshteinDistanceEngine
from src.compute.python_core.omni_pagerank_engine import OmniPageRankEngine

# ═══ Prime Sieve ═══
def test_sieve_basic():
    e = OmniPrimeSieveEngine()
    r = e.sieve_of_eratosthenes(30)
    assert r.is_ok()
    assert r.value["primes"] == [2,3,5,7,11,13,17,19,23,29]

def test_sieve_count():
    e = OmniPrimeSieveEngine()
    r = e.sieve_of_eratosthenes(100)
    assert r.is_ok() and r.value["count"] == 25

def test_is_prime_true():
    e = OmniPrimeSieveEngine()
    r = e.is_prime(97)
    assert r.is_ok() and r.value["is_prime"] is True

def test_is_prime_false():
    e = OmniPrimeSieveEngine()
    r = e.is_prime(100)
    assert r.is_ok() and r.value["is_prime"] is False

def test_factorize():
    e = OmniPrimeSieveEngine()
    r = e.factorize(60)
    assert r.is_ok()
    factors = {f["prime"]: f["exponent"] for f in r.value["factors"]}
    assert factors == {2: 2, 3: 1, 5: 1}

def test_prime_diagnostics():
    assert OmniPrimeSieveEngine().diagnostics()["status"] == "operational"

# ═══ Convolution Filter ═══
def test_conv_identity():
    e = OmniConvolutionFilterEngine()
    m = [[1,2,3],[4,5,6],[7,8,9]]
    r = e.apply_named_kernel(m, "identity")
    assert r.is_ok()
    assert r.value["output"][1][1] == 5.0

def test_conv_blur():
    e = OmniConvolutionFilterEngine()
    m = [[9,9,9],[9,9,9],[9,9,9]]
    r = e.apply_named_kernel(m, "blur_3x3")
    assert r.is_ok()
    assert abs(r.value["output"][1][1] - 9.0) < 0.01

def test_conv_custom():
    e = OmniConvolutionFilterEngine()
    m = [[0,0,0],[0,1,0],[0,0,0]]
    kernel = [[0,0,0],[0,2,0],[0,0,0]]
    r = e.convolve(m, kernel)
    assert r.is_ok() and r.value["output"][1][1] == 2.0

def test_conv_shape():
    e = OmniConvolutionFilterEngine()
    m = [[1]*5 for _ in range(5)]
    r = e.apply_named_kernel(m, "sharpen")
    assert r.is_ok() and r.value["output_shape"] == [5, 5]

def test_conv_diagnostics():
    assert OmniConvolutionFilterEngine().diagnostics()["status"] == "operational"

# ═══ Regex Parser ═══
def test_regex_match():
    e = OmniRegexParserEngine()
    r = e.match_all(r"\d+", "abc 123 def 456")
    assert r.is_ok() and r.value["count"] == 2

def test_regex_tokenize():
    e = OmniRegexParserEngine()
    r = e.tokenize("hello  world  foo")
    assert r.is_ok() and r.value["count"] == 3

def test_regex_replace():
    e = OmniRegexParserEngine()
    r = e.replace(r"\d", "X", "a1b2c3")
    assert r.is_ok() and r.value["result"] == "aXbXcX"

def test_regex_validate():
    e = OmniRegexParserEngine()
    r = e.validate_pattern(r"[a-z]+")
    assert r.is_ok() and r.value["valid"] is True

def test_regex_diagnostics():
    assert OmniRegexParserEngine().diagnostics()["status"] == "operational"

# ═══ Topological Sort ═══
def test_topo_basic():
    e = OmniTopologicalSortEngine()
    g = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    r = e.sort(g)
    assert r.is_ok()
    order = r.value["order"]
    assert order.index("A") < order.index("B")
    assert order.index("A") < order.index("C")

def test_topo_cycle():
    e = OmniTopologicalSortEngine()
    g = {"A": ["B"], "B": ["C"], "C": ["A"]}
    r = e.sort(g)
    assert not r.is_ok()

def test_topo_linear():
    e = OmniTopologicalSortEngine()
    g = {"A": ["B"], "B": ["C"], "C": []}
    r = e.sort(g)
    assert r.is_ok() and r.value["order"] == ["A", "B", "C"]

def test_topo_paths():
    e = OmniTopologicalSortEngine()
    g = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
    r = e.find_all_paths(g, "A", "D")
    assert r.is_ok() and r.value["count"] == 2

def test_topo_diagnostics():
    assert OmniTopologicalSortEngine().diagnostics()["status"] == "operational"

# ═══ HyperLogLog ═══
def test_hll_basic():
    h = OmniHyperloglogEngine(precision=10)
    for i in range(1000):
        h.add(f"item_{i}")
    r = h.estimate()
    assert r.is_ok()
    est = r.value["estimated_cardinality"]
    assert 800 < est < 1200  # ~20% error margin

def test_hll_empty():
    h = OmniHyperloglogEngine()
    r = h.estimate()
    assert r.is_ok() and r.value["estimated_cardinality"] == 0

def test_hll_duplicates():
    h = OmniHyperloglogEngine(precision=10)
    for _ in range(1000):
        h.add("same")
    r = h.estimate()
    assert r.is_ok() and r.value["estimated_cardinality"] <= 5

def test_hll_error_bound():
    h = OmniHyperloglogEngine(precision=14)
    r = h.estimate()
    assert r.is_ok() and r.value["relative_error"] < 0.1

def test_hll_diagnostics():
    assert OmniHyperloglogEngine().diagnostics()["status"] == "operational"

# ═══ BST ═══
def test_bst_insert_search():
    b = OmniBinarySearchTreeEngine()
    b.insert(5, "five"); b.insert(3, "three"); b.insert(7, "seven")
    r = b.search(3)
    assert r.is_ok() and r.value["found"] is True

def test_bst_not_found():
    b = OmniBinarySearchTreeEngine()
    b.insert(1)
    r = b.search(99)
    assert r.is_ok() and r.value["found"] is False

def test_bst_inorder():
    b = OmniBinarySearchTreeEngine()
    for k in [5,3,7,1,4]:
        b.insert(k)
    r = b.inorder()
    assert r.is_ok()
    keys = [item["key"] for item in r.value["traversal"]]
    assert keys == [1,3,4,5,7]

def test_bst_height():
    b = OmniBinarySearchTreeEngine()
    for k in [4,2,6,1,3,5,7]:
        b.insert(k)
    r = b.height()
    assert r.is_ok() and r.value["height"] == 2

def test_bst_diagnostics():
    assert OmniBinarySearchTreeEngine().diagnostics()["status"] == "operational"

# ═══ Moving Average ═══
def test_sma_basic():
    e = OmniMovingAverageEngine()
    r = e.sma([1,2,3,4,5], window=3)
    assert r.is_ok() and r.value["sma"] == [2.0, 3.0, 4.0]

def test_ema_basic():
    e = OmniMovingAverageEngine()
    r = e.ema([1,2,3,4,5], span=3)
    assert r.is_ok() and len(r.value["ema"]) == 5

def test_wma_basic():
    e = OmniMovingAverageEngine()
    r = e.wma([1,2,3,4,5], window=3)
    assert r.is_ok() and len(r.value["wma"]) == 3

def test_ma_invalid_window():
    e = OmniMovingAverageEngine()
    r = e.sma([1,2], window=5)
    assert not r.is_ok()

def test_ma_diagnostics():
    assert OmniMovingAverageEngine().diagnostics()["status"] == "operational"

# ═══ Additional Coverage ═══
def test_sieve_small():
    e = OmniPrimeSieveEngine()
    r = e.sieve_of_eratosthenes(1)
    assert r.is_ok() and r.value["primes"] == []

def test_conv_edge_detect():
    e = OmniConvolutionFilterEngine()
    m = [[0,0,0],[0,10,0],[0,0,0]]
    r = e.apply_named_kernel(m, "edge_detect")
    assert r.is_ok() and r.value["output"][1][1] == 80.0

def test_regex_groups():
    e = OmniRegexParserEngine()
    r = e.extract_groups(r"(\d+)-(\d+)", "date: 2026-04")
    assert r.is_ok() and r.value["matched"] is True
    assert r.value["positional_groups"] == ["2026", "04"]

def test_topo_single_node():
    e = OmniTopologicalSortEngine()
    r = e.sort({"A": []})
    assert r.is_ok() and r.value["order"] == ["A"]

def test_hll_add_returns_ok():
    h = OmniHyperloglogEngine()
    r = h.add("test_item")
    assert r.is_ok()

def test_bst_update_value():
    b = OmniBinarySearchTreeEngine()
    b.insert(10, "old")
    b.insert(10, "new")
    r = b.search(10)
    assert r.is_ok() and r.value["value"] == "new"

def test_ema_single():
    e = OmniMovingAverageEngine()
    r = e.ema([42.0], span=5)
    assert r.is_ok() and r.value["ema"] == [42.0]

def test_factorize_power_of_two():
    e = OmniPrimeSieveEngine()
    r = e.factorize(64)
    assert r.is_ok()
    assert r.value["factors"] == [{"prime": 2, "exponent": 6}]

def test_regex_invalid_pattern():
    e = OmniRegexParserEngine()
    r = e.validate_pattern(r"[invalid")
    assert r.is_ok() and r.value["valid"] is False

# ═══ Cross-Engine Validation ═══
def test_cross_levenshtein_symmetry():
    e = OmniLevenshteinDistanceEngine()
    r1 = e.compute_distance("abc", "xyz")
    r2 = e.compute_distance("xyz", "abc")
    assert r1.value["distance"] == r2.value["distance"]

def test_cross_pagerank_isolated():
    e = OmniPageRankEngine()
    g = {"A": [], "B": []}
    r = e.compute(g)
    assert r.is_ok()
    assert abs(r.value["ranks"]["A"] - r.value["ranks"]["B"]) < 1e-6

def test_cross_knapsack_greedy_suboptimal():
    e = OmniKnapsackDynamicProgrammingEngine()
    r = e.solve([6,3,4,2], [30,14,16,9], 10)
    assert r.is_ok() and r.value["max_value"] == 46

def test_cross_prime_factorize_prime():
    e = OmniPrimeSieveEngine()
    r = e.factorize(97)
    assert r.is_ok() and r.value["is_prime"] is True

def test_batch24_smoke():
    """Smoke test: All 10 engines instantiate and report operational."""
    engines = [OmniPrimeSieveEngine(), OmniConvolutionFilterEngine(), OmniRegexParserEngine(),
               OmniTopologicalSortEngine(), OmniHyperloglogEngine(), OmniBinarySearchTreeEngine(),
               OmniMovingAverageEngine(), OmniKnapsackDynamicProgrammingEngine(),
               OmniLevenshteinDistanceEngine(), OmniPageRankEngine()]
    for eng in engines:
        assert eng.diagnostics()["status"] == "operational"
