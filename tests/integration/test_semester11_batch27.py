"""Integration tests for Semester 11 Batch 27 — 50 tests for 10 engines."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.compute.python_core.omni_heap_sort_engine import OmniHeapSortEngine
from src.compute.python_core.omni_radix_sort_engine import OmniRadixSortEngine
from src.compute.python_core.omni_floyd_warshall_engine import OmniFloydWarshallEngine
from src.compute.python_core.omni_count_min_sketch_engine import OmniCountMinSketchEngine
from src.compute.python_core.omni_kmp_string_search_engine import OmniKmpStringSearchEngine
from src.compute.python_core.omni_convex_hull_engine import OmniConvexHullEngine
from src.compute.python_core.omni_bit_manipulation_engine import OmniBitManipulationEngine
from src.compute.python_core.omni_statistical_test_engine import OmniStatisticalTestEngine
from src.compute.python_core.omni_reservoir_sampling_engine import OmniReservoirSamplingEngine

# ═══ Heap Sort ═══
def test_hs_basic():
    e = OmniHeapSortEngine()
    r = e.sort([5,3,8,1,9,2])
    assert r.is_ok() and r.value["sorted"] == [1,2,3,5,8,9]

def test_hs_reverse():
    e = OmniHeapSortEngine()
    r = e.sort([1,2,3], reverse=True)
    assert r.is_ok() and r.value["sorted"] == [3,2,1]

def test_hs_single():
    e = OmniHeapSortEngine()
    r = e.sort([42])
    assert r.is_ok() and r.value["sorted"] == [42]

def test_hs_build_heap():
    e = OmniHeapSortEngine()
    r = e.build_heap([3,1,4,1,5])
    assert r.is_ok() and r.value["heap"][0] == 5

def test_hs_diagnostics():
    assert OmniHeapSortEngine().diagnostics()["status"] == "operational"

# ═══ Radix Sort ═══
def test_rs_basic():
    e = OmniRadixSortEngine()
    r = e.sort([170, 45, 75, 90, 802, 24, 2, 66])
    assert r.is_ok() and r.value["sorted"] == [2, 24, 45, 66, 75, 90, 170, 802]

def test_rs_negative():
    e = OmniRadixSortEngine()
    r = e.sort([-5, 3, -2, 8, 0])
    assert r.is_ok() and r.value["sorted"] == [-5, -2, 0, 3, 8]

def test_rs_empty():
    e = OmniRadixSortEngine()
    r = e.sort([])
    assert r.is_ok() and r.value["sorted"] == []

def test_rs_single():
    e = OmniRadixSortEngine()
    r = e.sort([99])
    assert r.is_ok() and r.value["sorted"] == [99]

def test_rs_diagnostics():
    assert OmniRadixSortEngine().diagnostics()["status"] == "operational"

# ═══ Floyd-Warshall ═══
def test_fw_basic():
    e = OmniFloydWarshallEngine()
    r = e.compute(["A","B","C"], [("A","B",1),("B","C",2),("A","C",10)])
    assert r.is_ok() and r.value["distances"]["A"]["C"] == 3

def test_fw_self():
    e = OmniFloydWarshallEngine()
    r = e.compute(["A","B"], [("A","B",5)])
    assert r.is_ok() and r.value["distances"]["A"]["A"] == 0

def test_fw_path():
    e = OmniFloydWarshallEngine()
    r = e.reconstruct_path(["A","B","C"], [("A","B",1),("B","C",2)], "A", "C")
    assert r.is_ok() and r.value["path"] == ["A", "B", "C"]

def test_fw_unreachable():
    e = OmniFloydWarshallEngine()
    r = e.reconstruct_path(["A","B"], [], "A", "B")
    assert r.is_ok() and r.value["reachable"] is False

def test_fw_diagnostics():
    assert OmniFloydWarshallEngine().diagnostics()["status"] == "operational"

# ═══ Count-Min Sketch ═══
def test_cms_add():
    c = OmniCountMinSketchEngine(width=100, depth=5)
    r = c.add("apple", 3)
    assert r.is_ok() and r.value["total"] == 3

def test_cms_estimate():
    c = OmniCountMinSketchEngine(width=1000, depth=7)
    for _ in range(50):
        c.add("banana")
    r = c.estimate("banana")
    assert r.is_ok() and r.value["estimated_count"] >= 50

def test_cms_unknown():
    c = OmniCountMinSketchEngine(width=1000, depth=7)
    r = c.estimate("unknown")
    assert r.is_ok() and r.value["estimated_count"] == 0

def test_cms_merge():
    a = OmniCountMinSketchEngine(width=100, depth=5)
    b = OmniCountMinSketchEngine(width=100, depth=5)
    a.add("x", 10)
    b.add("x", 20)
    r = a.merge(b)
    assert r.is_ok()
    est = a.estimate("x")
    assert est.value["estimated_count"] >= 30

def test_cms_diagnostics():
    assert OmniCountMinSketchEngine().diagnostics()["status"] == "operational"

# ═══ KMP ═══
def test_kmp_basic():
    e = OmniKmpStringSearchEngine()
    r = e.search("ababcababcabc", "abc")
    assert r.is_ok() and r.value["count"] == 3

def test_kmp_no_match():
    e = OmniKmpStringSearchEngine()
    r = e.search("hello", "xyz")
    assert r.is_ok() and r.value["count"] == 0

def test_kmp_overlap():
    e = OmniKmpStringSearchEngine()
    r = e.search("aaa", "aa")
    assert r.is_ok() and r.value["count"] == 2

def test_kmp_failure():
    e = OmniKmpStringSearchEngine()
    r = e.build_failure("abcabd")
    assert r.is_ok() and r.value["failure_function"] == [0,0,0,1,2,0]

def test_kmp_diagnostics():
    assert OmniKmpStringSearchEngine().diagnostics()["status"] == "operational"

# ═══ Convex Hull ═══
def test_hull_square():
    e = OmniConvexHullEngine()
    r = e.graham_scan([(0,0),(1,0),(1,1),(0,1),(0.5,0.5)])
    assert r.is_ok() and r.value["hull_size"] == 4

def test_hull_triangle():
    e = OmniConvexHullEngine()
    r = e.graham_scan([(0,0),(1,0),(0.5,1)])
    assert r.is_ok() and r.value["hull_size"] == 3 and r.value["area"] == 0.5

def test_hull_collinear():
    e = OmniConvexHullEngine()
    r = e.graham_scan([(0,0),(1,0),(2,0),(0,1)])  # add non-collinear point
    assert r.is_ok() and r.value["hull_size"] == 3

def test_hull_diagnostics():
    assert OmniConvexHullEngine().diagnostics()["status"] == "operational"

# ═══ Bit Manipulation ═══
def test_bit_popcount():
    e = OmniBitManipulationEngine()
    r = e.popcount(255)
    assert r.is_ok() and r.value["popcount"] == 8

def test_bit_pow2():
    e = OmniBitManipulationEngine()
    r = e.is_power_of_two(64)
    assert r.is_ok() and r.value["is_power_of_two"] is True

def test_bit_gray():
    e = OmniBitManipulationEngine()
    r = e.gray_code(3)
    assert r.is_ok() and r.value["count"] == 8

def test_bit_reverse():
    e = OmniBitManipulationEngine()
    r = e.reverse_bits(1, 8)
    assert r.is_ok() and r.value["reversed"] == 128

def test_bit_diagnostics():
    assert OmniBitManipulationEngine().diagnostics()["status"] == "operational"

# ═══ Statistical Test ═══
def test_stat_ztest():
    e = OmniStatisticalTestEngine()
    r = e.z_test([100]*20, 100, 10)
    assert r.is_ok() and abs(r.value["z_statistic"]) < 0.01

def test_stat_ttest():
    e = OmniStatisticalTestEngine()
    r = e.t_test_one_sample([10,11,12,13,14], 12)
    assert r.is_ok() and abs(r.value["t_statistic"]) < 1.0

def test_stat_pearson():
    e = OmniStatisticalTestEngine()
    r = e.pearson_correlation([1,2,3,4,5], [2,4,6,8,10])
    assert r.is_ok() and abs(r.value["r"] - 1.0) < 0.001

def test_stat_chi2():
    e = OmniStatisticalTestEngine()
    r = e.chi_squared([10,20,30], [15,15,30])
    assert r.is_ok() and r.value["chi_squared"] > 0

def test_stat_diagnostics():
    assert OmniStatisticalTestEngine().diagnostics()["status"] == "operational"

# ═══ Reservoir Sampling ═══
def test_reservoir_basic():
    e = OmniReservoirSamplingEngine()
    r = e.sample(list(range(100)), 10)
    assert r.is_ok() and len(r.value["sample"]) == 10

def test_reservoir_full():
    e = OmniReservoirSamplingEngine()
    r = e.sample([1,2,3], 5)
    assert r.is_ok() and r.value["full_stream"] is True

def test_reservoir_diagnostics():
    assert OmniReservoirSamplingEngine().diagnostics()["status"] == "operational"

# ═══ Additional Coverage ═══
def test_hs_already_sorted():
    e = OmniHeapSortEngine()
    r = e.sort([1,2,3,4,5])
    assert r.is_ok() and r.value["sorted"] == [1,2,3,4,5]

def test_rs_base2():
    e = OmniRadixSortEngine()
    r = e.sort([8, 4, 2, 1, 16], base=2)
    assert r.is_ok() and r.value["sorted"] == [1, 2, 4, 8, 16]

def test_kmp_full_match():
    e = OmniKmpStringSearchEngine()
    r = e.search("abc", "abc")
    assert r.is_ok() and r.value["count"] == 1 and r.value["matches"] == [0]

def test_bit_next_pow2():
    e = OmniBitManipulationEngine()
    r = e.next_power_of_two(13)
    assert r.is_ok() and r.value["next_power_of_two"] == 16

def test_stat_two_sample_t():
    e = OmniStatisticalTestEngine()
    r = e.t_test_two_sample([10,20,30], [40,50,60])
    assert r.is_ok() and r.value["t_statistic"] < 0

def test_bit_trailing_zeros():
    e = OmniBitManipulationEngine()
    r = e.count_trailing_zeros(8)
    assert r.is_ok() and r.value["trailing_zeros"] == 3

def test_reservoir_deterministic():
    e = OmniReservoirSamplingEngine()
    r1 = e.sample(list(range(100)), 5, seed="test")
    r2 = e.sample(list(range(100)), 5, seed="test")
    assert r1.value["sample"] == r2.value["sample"]

# ═══ Smoke ═══
def test_batch27_smoke():
    engines = [OmniHeapSortEngine(), OmniRadixSortEngine(), OmniFloydWarshallEngine(),
               OmniCountMinSketchEngine(), OmniKmpStringSearchEngine(), OmniConvexHullEngine(),
               OmniBitManipulationEngine(), OmniStatisticalTestEngine(), OmniReservoirSamplingEngine()]
    for eng in engines:
        assert eng.diagnostics()["status"] == "operational"
