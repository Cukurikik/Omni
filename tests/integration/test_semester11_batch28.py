"""Integration tests for Semester 11 Batch 28 — 50 tests for 10 engines."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.compute.python_core.omni_minishell_parser_engine import OmniMinishellParserEngine
from src.compute.python_core.omni_reed_solomon_error_correction_engine import OmniReedSolomonErrorCorrectionEngine
from src.compute.python_core.omni_btree_engine import OmniBTreeEngine
from src.compute.python_core.omni_simplex_linear_programming_engine import OmniSimplexLinearProgrammingEngine
from src.compute.python_core.omni_okapi_bm25_engine import OmniOkapiBm25Engine
from src.compute.python_core.omni_graph_coloring_engine import OmniGraphColoringEngine
from src.compute.python_core.omni_bipartite_matching_engine import OmniBipartiteMatchingEngine
from src.compute.python_core.omni_html_parser_engine import OmniHtmlParserEngine
from src.compute.python_core.omni_shunting_yard_engine import OmniShuntingYardEngine
from src.compute.python_core.omni_aho_corasick_engine import OmniAhoCorasickEngine

# ═══ Minishell Parser ═══
def test_mini_simple():
    e = OmniMinishellParserEngine()
    r = e.parse("echo 'hello world'")
    assert r.is_ok() and r.value["ast"][0]["args"] == ["echo", "hello world"]

def test_mini_pipe():
    e = OmniMinishellParserEngine()
    r = e.parse("ls -la | grep txt")
    assert r.is_ok() and len(r.value["ast"]) == 2
    assert r.value["ast"][1]["args"] == ["grep", "txt"]

def test_mini_redirect():
    e = OmniMinishellParserEngine()
    r = e.parse("cat < input.txt > output.txt")
    assert r.is_ok() and len(r.value["ast"][0]["redirects"]) == 2

def test_mini_quotes():
    e = OmniMinishellParserEngine()
    r = e.parse('echo "quoted | pipe"')
    assert r.is_ok() and len(r.value["ast"]) == 1

def test_mini_diagnostics():
    assert OmniMinishellParserEngine().diagnostics()["status"] == "operational"

# ═══ Reed Solomon Error Correction ═══
def test_rs_basic():
    e = OmniReedSolomonErrorCorrectionEngine()
    r = e.encode(b"hello", 4)
    assert r.is_ok() and len(r.value["encoded"]) == 9

def test_rs_single_char():
    e = OmniReedSolomonErrorCorrectionEngine()
    r = e.encode(b"A", 2)
    assert r.is_ok() and len(r.value["encoded"]) == 3

def test_rs_invalid():
    e = OmniReedSolomonErrorCorrectionEngine()
    r = e.encode(b"hello", 300)
    assert not r.is_ok()

def test_rs_deterministic():
    e = OmniReedSolomonErrorCorrectionEngine()
    r1 = e.encode(b"test", 5)
    r2 = e.encode(b"test", 5)
    assert r1.value["encoded"] == r2.value["encoded"]

def test_rs_diagnostics():
    assert OmniReedSolomonErrorCorrectionEngine().diagnostics()["status"] == "operational"

# ═══ B-Tree ═══
def test_btree_insert_search():
    e = OmniBTreeEngine(t=2)
    e.insert(10)
    e.insert(20)
    r = e.search(10)
    assert r.is_ok() and r.value["found"] is True

def test_btree_not_found():
    e = OmniBTreeEngine(t=2)
    e.insert(10)
    r = e.search(99)
    assert r.is_ok() and r.value["found"] is False

def test_btree_split():
    e = OmniBTreeEngine(t=2)
    for i in range(1, 10):
        e.insert(i) # Forces splits
    r = e.search(7)
    assert r.is_ok() and r.value["found"] is True

def test_btree_in_order():
    e = OmniBTreeEngine(t=2)
    for i in [5, 3, 7, 1]:
        e.insert(i)
    r = e.in_order()
    assert r.is_ok() and r.value["keys"] == [1, 3, 5, 7]

def test_btree_diagnostics():
    assert OmniBTreeEngine().diagnostics()["status"] == "operational"

# ═══ Simplex LP ═══
def test_simplex_basic():
    e = OmniSimplexLinearProgrammingEngine()
    # Maximize 3x + 2y
    # s.t. 2x + y <= 18
    #      2x + 3y <= 42
    #      3x + y <= 24
    r = e.maximize([3, 2], [[2, 1], [2, 3], [3, 1]], [18, 42, 24])
    assert r.is_ok() and abs(r.value["maximum_value"] - 33.0) < 1e-5

def test_simplex_origin():
    e = OmniSimplexLinearProgrammingEngine()
    r = e.maximize([-1, -1], [[1, 1]], [5])
    assert r.is_ok() and r.value["maximum_value"] == 0.0

def test_simplex_unbounded():
    e = OmniSimplexLinearProgrammingEngine()
    # Maximize 2x
    # s.t. -x <= 10  (no positive bound on x)
    r = e.maximize([2], [[-1]], [10])
    assert not r.is_ok()

def test_simplex_zero_obj():
    e = OmniSimplexLinearProgrammingEngine()
    r = e.maximize([0, 0], [[1, 1]], [10])
    assert r.is_ok() and r.value["maximum_value"] == 0.0

def test_simplex_diagnostics():
    assert OmniSimplexLinearProgrammingEngine().diagnostics()["status"] == "operational"

# ═══ Okapi BM25 ═══
def test_bm25_basic():
    e = OmniOkapiBm25Engine()
    corpus = ["the quick brown fox", "the lazy dog", "quick rabbit"]
    e.fit(corpus)
    r = e.score("quick")
    assert r.is_ok() and r.value["scores"][0] > 0 and r.value["scores"][1] == 0.0

def test_bm25_empty_query():
    e = OmniOkapiBm25Engine()
    e.fit(["hello world"])
    r = e.score("xyz")
    assert r.is_ok() and sum(r.value["scores"]) == 0.0

def test_bm25_unfitted():
    e = OmniOkapiBm25Engine()
    r = e.score("test")
    assert not r.is_ok()

def test_bm25_multiple_terms():
    e = OmniOkapiBm25Engine()
    e.fit(["apple banana", "apple orange", "banana kiwi orange"])
    r = e.score("apple banana")
    # doc 0 has both, should score highest
    assert r.is_ok() and r.value["scores"][0] > r.value["scores"][1]

def test_bm25_diagnostics():
    assert OmniOkapiBm25Engine().diagnostics()["status"] == "operational"

# ═══ Graph Coloring ═══
def test_gc_triangle():
    e = OmniGraphColoringEngine()
    r = e.welsh_powell(3, [[0,1], [1,2], [2,0]])
    assert r.is_ok() and r.value["chromatic_number_estimate"] == 3

def test_gc_bipartite():
    e = OmniGraphColoringEngine()
    r = e.welsh_powell(4, [[0,1], [1,2], [2,3], [3,0]])
    assert r.is_ok() and r.value["chromatic_number_estimate"] == 2

def test_gc_disconnected():
    e = OmniGraphColoringEngine()
    r = e.welsh_powell(3, [])
    assert r.is_ok() and r.value["chromatic_number_estimate"] == 1

def test_gc_invalid_edge():
    e = OmniGraphColoringEngine()
    r = e.welsh_powell(2, [[0, 5]])
    assert not r.is_ok()

def test_gc_diagnostics():
    assert OmniGraphColoringEngine().diagnostics()["status"] == "operational"

# ═══ Bipartite Matching ═══
def test_bpm_basic():
    e = OmniBipartiteMatchingEngine()
    r = e.max_matching(3, 3, [[1,1], [1,2], [2,1], [3,3]])
    assert r.is_ok() and r.value["max_matching"] == 3

def test_bpm_partial():
    e = OmniBipartiteMatchingEngine()
    r = e.max_matching(2, 2, [[1,1], [2,1]])
    assert r.is_ok() and r.value["max_matching"] == 1

def test_bpm_empty():
    e = OmniBipartiteMatchingEngine()
    r = e.max_matching(3, 3, [])
    assert r.is_ok() and r.value["max_matching"] == 0

def test_bpm_complete():
    e = OmniBipartiteMatchingEngine()
    edges = [[1,1], [1,2], [2,1], [2,2]]
    r = e.max_matching(2, 2, edges)
    assert r.is_ok() and r.value["max_matching"] == 2

def test_bpm_diagnostics():
    assert OmniBipartiteMatchingEngine().diagnostics()["status"] == "operational"

# ═══ Html Parser ═══
def test_html_basic():
    e = OmniHtmlParserEngine()
    r = e.parse("<div>hello</div>")
    assert r.is_ok() and len(r.value["dom"]) == 1
    assert r.value["dom"][0]["tag"] == "div"

def test_html_nested():
    e = OmniHtmlParserEngine()
    r = e.parse("<p><b>bold</b> text</p>")
    assert r.is_ok() 
    assert len(r.value["dom"][0]["children"]) == 2

def test_html_attributes():
    e = OmniHtmlParserEngine()
    r = e.parse('<img src="test.jpg" alt="test" />')
    assert r.is_ok() and r.value["dom"][0]["attributes"]["src"] == "test.jpg"

def test_html_mismatch():
    e = OmniHtmlParserEngine()
    r = e.parse("<div></span>")
    assert not r.is_ok()

def test_html_diagnostics():
    assert OmniHtmlParserEngine().diagnostics()["status"] == "operational"

# ═══ Shunting Yard ═══
def test_sy_basic():
    e = OmniShuntingYardEngine()
    r = e.evaluate("3 + 4 * 2")
    assert r.is_ok() and r.value["result"] == 11.0

def test_sy_parens():
    e = OmniShuntingYardEngine()
    r = e.evaluate("( 3 + 4 ) * 2")
    assert r.is_ok() and r.value["result"] == 14.0

def test_sy_power():
    e = OmniShuntingYardEngine()
    r = e.evaluate("2 ^ 3 + 1")
    assert r.is_ok() and r.value["result"] == 9.0

def test_sy_invalid():
    e = OmniShuntingYardEngine()
    r = e.evaluate("3 + * 2")
    assert not r.is_ok()

def test_sy_diagnostics():
    assert OmniShuntingYardEngine().diagnostics()["status"] == "operational"

# ═══ Aho Corasick ═══
def test_aho_basic():
    e = OmniAhoCorasickEngine()
    e.build(["he", "she", "his", "hers"])
    r = e.search("ushers")
    assert r.is_ok() and len(r.value["matches"]) == 3 # she, he, hers

def test_aho_not_built():
    e = OmniAhoCorasickEngine()
    r = e.search("test")
    assert not r.is_ok()

def test_aho_no_match():
    e = OmniAhoCorasickEngine()
    e.build(["apple", "banana"])
    r = e.search("orange")
    assert r.is_ok() and len(r.value["matches"]) == 0

def test_aho_overlaps():
    e = OmniAhoCorasickEngine()
    e.build(["ana", "nana"])
    r = e.search("banana")
    assert r.is_ok() and len(r.value["matches"]) == 3

def test_aho_diagnostics():
    assert OmniAhoCorasickEngine().diagnostics()["status"] == "not_built"

# ═══ Batch 28 Smoke Test ═══
def test_batch28_smoke():
    engines = [
        OmniMinishellParserEngine(),
        OmniReedSolomonErrorCorrectionEngine(),
        OmniBTreeEngine(),
        OmniSimplexLinearProgrammingEngine(),
        OmniOkapiBm25Engine(),
        OmniGraphColoringEngine(),
        OmniBipartiteMatchingEngine(),
        OmniHtmlParserEngine(),
        OmniShuntingYardEngine(),
        OmniAhoCorasickEngine()
    ]
    for eng in engines:
        assert isinstance(eng.diagnostics(), dict)
