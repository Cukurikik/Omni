"""Integration tests for Semester 11 Batch 22 — 50 tests for 10 engines."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.compute.python_core.omni_dijkstra_shortest_path_engine import OmniDijkstraShortestPathEngine
from src.compute.python_core.omni_lru_cache_eviction_engine import OmniLruCacheEvictionEngine
from src.compute.python_core.omni_rsa_cryptography_engine import OmniRsaCryptographyEngine
from src.compute.python_core.omni_astar_pathfinding_engine import OmniAstarPathfindingEngine
from src.compute.python_core.omni_huffman_compression_engine import OmniHuffmanCompressionEngine
from src.compute.python_core.omni_bloom_filter_engine import OmniBloomFilterEngine
from src.compute.python_core.omni_kmeans_clustering_engine import OmniKmeansClusteringEngine
from src.compute.python_core.omni_mergesort_engine import OmniMergesortEngine
from src.compute.python_core.omni_levenshtein_distance_engine import OmniLevenshteinDistanceEngine
from src.compute.python_core.omni_pagerank_engine import OmniPageRankEngine

# ═══ Dijkstra ═══
def test_dijkstra_simple():
    e = OmniDijkstraShortestPathEngine()
    g = {"A": {"B": 1, "C": 4}, "B": {"C": 2, "D": 5}, "C": {"D": 1}, "D": {}}
    r = e.compute_shortest_paths(g, "A")
    assert r.is_ok()
    assert r.value["distances"]["D"] == 4.0

def test_dijkstra_path_reconstruction():
    e = OmniDijkstraShortestPathEngine()
    g = {"A": {"B": 1, "C": 4}, "B": {"C": 2, "D": 5}, "C": {"D": 1}, "D": {}}
    r = e.compute_shortest_paths(g, "A")
    p = e.reconstruct_path(r.value["predecessors"], "D")
    assert p.is_ok()
    assert p.value["path"] == ["A", "B", "C", "D"]

def test_dijkstra_negative_weight():
    e = OmniDijkstraShortestPathEngine()
    g = {"A": {"B": -1}, "B": {}}
    r = e.compute_shortest_paths(g, "A")
    assert not r.is_ok()

def test_dijkstra_single_node():
    e = OmniDijkstraShortestPathEngine()
    g = {"A": {}}
    r = e.compute_shortest_paths(g, "A")
    assert r.is_ok()
    assert r.value["distances"]["A"] == 0.0

def test_dijkstra_diagnostics():
    e = OmniDijkstraShortestPathEngine()
    d = e.diagnostics()
    assert d["status"] == "operational"

# ═══ LRU Cache ═══
def test_lru_hit():
    c = OmniLruCacheEvictionEngine(capacity=2)
    c.put("a", 1)
    r = c.get("a")
    assert r.is_ok() and r.value["hit"] is True and r.value["value"] == 1

def test_lru_miss():
    c = OmniLruCacheEvictionEngine(capacity=2)
    r = c.get("x")
    assert r.is_ok() and r.value["hit"] is False

def test_lru_eviction():
    c = OmniLruCacheEvictionEngine(capacity=2)
    c.put("a", 1)
    c.put("b", 2)
    r = c.put("c", 3)
    assert r.is_ok() and r.value["evicted"]["key"] == "a"

def test_lru_stats():
    c = OmniLruCacheEvictionEngine(capacity=3)
    c.put("a", 1); c.get("a"); c.get("x")
    r = c.get_stats()
    assert r.is_ok() and r.value["hits"] == 1 and r.value["misses"] == 1

def test_lru_diagnostics():
    c = OmniLruCacheEvictionEngine(capacity=5)
    assert c.diagnostics()["status"] == "operational"

# ═══ RSA ═══
def test_rsa_keygen():
    e = OmniRsaCryptographyEngine()
    r = e.generate_keys(61, 53)
    assert r.is_ok()
    assert r.value["public_key"]["n"] == 61 * 53

def test_rsa_encrypt_decrypt():
    e = OmniRsaCryptographyEngine()
    keys = e.generate_keys(61, 53)
    msg = 42
    enc = e.encrypt(msg, keys.value["public_key"])
    dec = e.decrypt(enc.value["ciphertext"], keys.value["private_key"])
    assert dec.value["plaintext"] == msg

def test_rsa_non_prime():
    e = OmniRsaCryptographyEngine()
    r = e.generate_keys(4, 53)
    assert not r.is_ok()

def test_rsa_same_primes():
    e = OmniRsaCryptographyEngine()
    r = e.generate_keys(53, 53)
    assert not r.is_ok()

def test_rsa_diagnostics():
    assert OmniRsaCryptographyEngine().diagnostics()["status"] == "operational"

# ═══ A* Pathfinding ═══
def test_astar_simple():
    e = OmniAstarPathfindingEngine()
    grid = [[0,0,0],[0,1,0],[0,0,0]]
    r = e.find_path(grid, (0,0), (2,2))
    assert r.is_ok() and r.value["path"] is not None

def test_astar_blocked():
    e = OmniAstarPathfindingEngine()
    grid = [[0,1],[1,0]]
    r = e.find_path(grid, (0,0), (1,1))
    assert r.is_ok() and r.value["path"] is None

def test_astar_straight():
    e = OmniAstarPathfindingEngine()
    grid = [[0,0,0,0]]
    r = e.find_path(grid, (0,0), (0,3))
    assert r.is_ok() and r.value["cost"] == 3.0

def test_astar_diagonal():
    e = OmniAstarPathfindingEngine()
    grid = [[0,0],[0,0]]
    r = e.find_path(grid, (0,0), (1,1), allow_diagonal=True)
    assert r.is_ok() and r.value["path_length"] == 2

def test_astar_diagnostics():
    assert OmniAstarPathfindingEngine().diagnostics()["status"] == "operational"

# ═══ Huffman ═══
def test_huffman_compress():
    e = OmniHuffmanCompressionEngine()
    r = e.compress("aaabbc")
    assert r.is_ok() and r.value["compression_ratio"] < 1.0

def test_huffman_roundtrip():
    e = OmniHuffmanCompressionEngine()
    text = "hello world"
    c = e.compress(text)
    d = e.decompress(c.value["encoded"], c.value["codes"])
    assert d.is_ok() and d.value["decoded"] == text

def test_huffman_single_char():
    e = OmniHuffmanCompressionEngine()
    r = e.compress("aaa")
    assert r.is_ok() and r.value["unique_chars"] == 1

def test_huffman_empty():
    e = OmniHuffmanCompressionEngine()
    r = e.compress("")
    assert not r.is_ok()

def test_huffman_diagnostics():
    assert OmniHuffmanCompressionEngine().diagnostics()["status"] == "operational"

# ═══ Bloom Filter ═══
def test_bloom_add_contains():
    b = OmniBloomFilterEngine(expected_items=100, false_positive_rate=0.01)
    b.add("hello")
    r = b.contains("hello")
    assert r.is_ok() and r.value["probably_contains"] is True

def test_bloom_not_contains():
    b = OmniBloomFilterEngine(expected_items=100)
    r = b.contains("missing")
    assert r.is_ok() and r.value["probably_contains"] is False

def test_bloom_stats():
    b = OmniBloomFilterEngine(expected_items=10)
    for i in range(5):
        b.add(f"item_{i}")
    r = b.get_stats()
    assert r.is_ok() and r.value["items_added"] == 5

def test_bloom_optimal_size():
    b = OmniBloomFilterEngine(expected_items=1000, false_positive_rate=0.001)
    assert b.m > 1000

def test_bloom_diagnostics():
    assert OmniBloomFilterEngine().diagnostics()["status"] == "operational"

# ═══ K-Means ═══
def test_kmeans_basic():
    e = OmniKmeansClusteringEngine()
    data = [[0,0],[0,1],[10,10],[10,11]]
    r = e.fit(data, k=2)
    assert r.is_ok() and r.value["k"] == 2

def test_kmeans_labels():
    e = OmniKmeansClusteringEngine()
    data = [[0,0],[0,1],[100,100],[100,101]]
    r = e.fit(data, k=2)
    assert r.is_ok()
    labels = r.value["labels"]
    assert labels[0] == labels[1] and labels[2] == labels[3]

def test_kmeans_single_cluster():
    e = OmniKmeansClusteringEngine()
    r = e.fit([[1,2],[3,4],[5,6]], k=1)
    assert r.is_ok() and r.value["inertia"] > 0

def test_kmeans_invalid_k():
    e = OmniKmeansClusteringEngine()
    r = e.fit([[1]], k=5)
    assert not r.is_ok()

def test_kmeans_diagnostics():
    assert OmniKmeansClusteringEngine().diagnostics()["status"] == "operational"

# ═══ Merge Sort ═══
def test_mergesort_basic():
    e = OmniMergesortEngine()
    r = e.sort([3,1,4,1,5,9,2,6])
    assert r.is_ok() and r.value["sorted"] == [1,1,2,3,4,5,6,9]

def test_mergesort_reverse():
    e = OmniMergesortEngine()
    r = e.sort([1,2,3], reverse=True)
    assert r.is_ok() and r.value["sorted"] == [3,2,1]

def test_mergesort_empty():
    e = OmniMergesortEngine()
    r = e.sort([])
    assert r.is_ok() and r.value["sorted"] == []

def test_mergesort_stable():
    e = OmniMergesortEngine()
    r = e.sort([5,5,5])
    assert r.is_ok() and r.value["stable"] is True

def test_mergesort_diagnostics():
    assert OmniMergesortEngine().diagnostics()["status"] == "operational"

# ═══ Levenshtein ═══
def test_levenshtein_identical():
    e = OmniLevenshteinDistanceEngine()
    r = e.compute_distance("hello", "hello")
    assert r.is_ok() and r.value["distance"] == 0

def test_levenshtein_basic():
    e = OmniLevenshteinDistanceEngine()
    r = e.compute_distance("kitten", "sitting")
    assert r.is_ok() and r.value["distance"] == 3

def test_levenshtein_operations():
    e = OmniLevenshteinDistanceEngine()
    r = e.compute_edit_operations("abc", "aec")
    assert r.is_ok() and r.value["operation_count"] == 1

def test_levenshtein_empty():
    e = OmniLevenshteinDistanceEngine()
    r = e.compute_distance("", "abc")
    assert r.is_ok() and r.value["distance"] == 3

def test_levenshtein_diagnostics():
    assert OmniLevenshteinDistanceEngine().diagnostics()["status"] == "operational"

# ═══ PageRank ═══
def test_pagerank_basic():
    e = OmniPageRankEngine()
    g = {"A": ["B", "C"], "B": ["C"], "C": ["A"], "D": ["C"]}
    r = e.compute(g)
    assert r.is_ok() and r.value["total_nodes"] == 4

def test_pagerank_convergence():
    e = OmniPageRankEngine()
    g = {"A": ["B"], "B": ["C"], "C": ["A"]}
    r = e.compute(g)
    assert r.is_ok() and r.value["converged"] is True

def test_pagerank_sum():
    e = OmniPageRankEngine()
    g = {"A": ["B"], "B": ["A"]}
    r = e.compute(g)
    total = sum(r.value["ranks"].values())
    assert abs(total - 1.0) < 1e-6

def test_pagerank_empty():
    e = OmniPageRankEngine()
    r = e.compute({})
    assert not r.is_ok()

def test_pagerank_diagnostics():
    assert OmniPageRankEngine().diagnostics()["status"] == "operational"
