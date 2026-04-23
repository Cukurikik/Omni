"""Integration tests for Semester 11 Batch 23 — 50 tests for 10 engines."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.compute.python_core.omni_knapsack_dp_engine import OmniKnapsackDynamicProgrammingEngine
from src.compute.python_core.omni_markov_chain_engine import OmniMarkovChainEngine
from src.compute.python_core.omni_tokenizer_bpe_engine import OmniTokenizerBpeEngine
from src.compute.python_core.omni_consistent_hashing_engine import OmniConsistentHashingEngine
from src.compute.python_core.omni_matrix_decomposition_engine import OmniMatrixDecompositionEngine
from src.compute.python_core.omni_genetic_algorithm_engine import OmniGeneticAlgorithmEngine
from src.compute.python_core.omni_fibonacci_heap_engine import OmniFibonacciHeapEngine
from src.compute.python_core.omni_json_schema_validator_engine import OmniJsonSchemaValidatorEngine
from src.compute.python_core.omni_naive_bayes_classifier_engine import OmniNaiveBayesClassifierEngine
from src.compute.python_core.omni_tfidf_vectorizer_engine import OmniTfIdfVectorizerEngine

# ═══ Knapsack ═══
def test_knapsack_basic():
    e = OmniKnapsackDynamicProgrammingEngine()
    r = e.solve([2,3,4,5], [3,4,5,6], 5)
    assert r.is_ok() and r.value["max_value"] == 7

def test_knapsack_exact_fit():
    e = OmniKnapsackDynamicProgrammingEngine()
    r = e.solve([10], [100], 10)
    assert r.is_ok() and r.value["max_value"] == 100

def test_knapsack_zero_capacity():
    e = OmniKnapsackDynamicProgrammingEngine()
    r = e.solve([1,2], [3,4], 0)
    assert r.is_ok() and r.value["max_value"] == 0

def test_knapsack_all_fit():
    e = OmniKnapsackDynamicProgrammingEngine()
    r = e.solve([1,1,1], [10,20,30], 10)
    assert r.is_ok() and r.value["max_value"] == 60

def test_knapsack_diagnostics():
    assert OmniKnapsackDynamicProgrammingEngine().diagnostics()["status"] == "operational"

# ═══ Markov Chain ═══
def test_markov_validate():
    e = OmniMarkovChainEngine()
    r = e.validate_transition_matrix([[0.5,0.5],[0.3,0.7]])
    assert r.is_ok() and r.value["valid"] is True

def test_markov_invalid_row():
    e = OmniMarkovChainEngine()
    r = e.validate_transition_matrix([[0.5,0.3],[0.3,0.7]])
    assert not r.is_ok()

def test_markov_nstep():
    e = OmniMarkovChainEngine()
    r = e.n_step_transition([[0.5,0.5],[0.3,0.7]], 1)
    assert r.is_ok()
    assert abs(r.value["transition_matrix"][0][0] - 0.5) < 1e-6

def test_markov_stationary():
    e = OmniMarkovChainEngine()
    r = e.stationary_distribution([[0.5,0.5],[0.3,0.7]])
    assert r.is_ok() and r.value["converged"] is True
    assert abs(sum(r.value["distribution"]) - 1.0) < 1e-6

def test_markov_diagnostics():
    assert OmniMarkovChainEngine().diagnostics()["status"] == "operational"

# ═══ BPE Tokenizer ═══
def test_bpe_train():
    e = OmniTokenizerBpeEngine()
    r = e.train("aaabdaaabac", num_merges=5)
    assert r.is_ok() and r.value["vocab_size"] > 0

def test_bpe_compression():
    e = OmniTokenizerBpeEngine()
    r = e.train("aaabdaaabac", num_merges=10)
    assert r.is_ok() and r.value["compression_ratio"] > 1.0

def test_bpe_encode():
    e = OmniTokenizerBpeEngine()
    r = e.train("abababab", num_merges=3)
    enc = e.encode("abab", r.value["merge_rules"])
    assert enc.is_ok() and enc.value["token_count"] <= 4

def test_bpe_empty():
    e = OmniTokenizerBpeEngine()
    r = e.train("")
    assert not r.is_ok()

def test_bpe_diagnostics():
    assert OmniTokenizerBpeEngine().diagnostics()["status"] == "operational"

# ═══ Consistent Hashing ═══
def test_ch_add_node():
    e = OmniConsistentHashingEngine(replicas=10)
    r = e.add_node("server1")
    assert r.is_ok() and r.value["virtual_nodes_added"] == 10

def test_ch_get_node():
    e = OmniConsistentHashingEngine(replicas=10)
    e.add_node("server1")
    r = e.get_node("my_key")
    assert r.is_ok() and r.value["node"] == "server1"

def test_ch_distribution():
    e = OmniConsistentHashingEngine(replicas=50)
    e.add_node("s1"); e.add_node("s2")
    r = e.get_distribution([f"key_{i}" for i in range(100)])
    assert r.is_ok() and r.value["total_keys"] == 100

def test_ch_remove():
    e = OmniConsistentHashingEngine(replicas=10)
    e.add_node("s1"); e.add_node("s2")
    r = e.remove_node("s1")
    assert r.is_ok()

def test_ch_diagnostics():
    assert OmniConsistentHashingEngine().diagnostics()["status"] == "operational"

# ═══ Matrix Decomposition ═══
def test_lu_basic():
    e = OmniMatrixDecompositionEngine()
    r = e.lu_decompose([[2,1],[4,3]])
    assert r.is_ok() and r.value["n"] == 2

def test_lu_determinant():
    e = OmniMatrixDecompositionEngine()
    r = e.determinant([[1,2],[3,4]])
    assert r.is_ok() and abs(r.value["determinant"] - (-2)) < 1e-6

def test_lu_solve():
    e = OmniMatrixDecompositionEngine()
    r = e.solve([[2,1],[5,3]], [4,7])
    assert r.is_ok()
    x = r.value["solution"]
    assert abs(x[0] - 5.0) < 1e-6 and abs(x[1] - (-6.0)) < 1e-6

def test_lu_singular():
    e = OmniMatrixDecompositionEngine()
    r = e.lu_decompose([[1,2],[2,4]])
    assert not r.is_ok()

def test_lu_diagnostics():
    assert OmniMatrixDecompositionEngine().diagnostics()["status"] == "operational"

# ═══ Genetic Algorithm ═══
def test_ga_onemax():
    e = OmniGeneticAlgorithmEngine()
    r = e.optimize(lambda c: sum(c), gene_length=10, pop_size=20, generations=50)
    assert r.is_ok() and r.value["best_fitness"] > 0

def test_ga_convergence():
    e = OmniGeneticAlgorithmEngine()
    r = e.optimize(lambda c: sum(c), gene_length=5, pop_size=30, generations=100)
    assert r.is_ok() and r.value["best_fitness"] >= 3

def test_ga_history():
    e = OmniGeneticAlgorithmEngine()
    r = e.optimize(lambda c: sum(c), gene_length=5, pop_size=10, generations=20)
    assert r.is_ok() and len(r.value["history_sample"]) > 0

def test_ga_invalid():
    e = OmniGeneticAlgorithmEngine()
    r = e.optimize(lambda c: sum(c), gene_length=0)
    assert not r.is_ok()

def test_ga_diagnostics():
    assert OmniGeneticAlgorithmEngine().diagnostics()["status"] == "operational"

# ═══ Fibonacci ═══
def test_fib_iterative():
    e = OmniFibonacciHeapEngine()
    r = e.compute_iterative(10)
    assert r.is_ok() and r.value["fibonacci"] == 55

def test_fib_matrix():
    e = OmniFibonacciHeapEngine()
    r = e.compute_matrix(10)
    assert r.is_ok() and r.value["fibonacci"] == 55

def test_fib_sequence():
    e = OmniFibonacciHeapEngine()
    r = e.generate_sequence(8)
    assert r.is_ok() and r.value["sequence"] == [0,1,1,2,3,5,8,13]

def test_fib_zero():
    e = OmniFibonacciHeapEngine()
    r = e.compute_iterative(0)
    assert r.is_ok() and r.value["fibonacci"] == 0

def test_fib_diagnostics():
    assert OmniFibonacciHeapEngine().diagnostics()["status"] == "operational"

# ═══ JSON Schema Validator ═══
def test_schema_valid():
    e = OmniJsonSchemaValidatorEngine()
    schema = {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}
    r = e.validate({"name": "test"}, schema)
    assert r.is_ok() and r.value["valid"] is True

def test_schema_missing_required():
    e = OmniJsonSchemaValidatorEngine()
    schema = {"type": "object", "required": ["name"]}
    r = e.validate({}, schema)
    assert r.is_ok() and r.value["valid"] is False

def test_schema_string_min():
    e = OmniJsonSchemaValidatorEngine()
    r = e.validate("ab", {"type": "string", "minLength": 3})
    assert r.is_ok() and r.value["valid"] is False

def test_schema_number_range():
    e = OmniJsonSchemaValidatorEngine()
    r = e.validate(5, {"type": "number", "minimum": 1, "maximum": 10})
    assert r.is_ok() and r.value["valid"] is True

def test_schema_diagnostics():
    assert OmniJsonSchemaValidatorEngine().diagnostics()["status"] == "operational"

# ═══ Naive Bayes ═══
def test_nb_fit():
    e = OmniNaiveBayesClassifierEngine()
    X = [[1,1],[2,2],[10,10],[11,11]]
    y = [0,0,1,1]
    r = e.fit(X, y)
    assert r.is_ok() and len(r.value["classes"]) == 2

def test_nb_predict():
    e = OmniNaiveBayesClassifierEngine()
    X = [[1,1],[2,2],[10,10],[11,11]]
    y = [0,0,1,1]
    e.fit(X, y)
    r = e.predict([[1.5,1.5],[10.5,10.5]])
    assert r.is_ok() and r.value["predictions"] == [0, 1]

def test_nb_untrained():
    e = OmniNaiveBayesClassifierEngine()
    r = e.predict([[1,2]])
    assert not r.is_ok()

def test_nb_multi_class():
    e = OmniNaiveBayesClassifierEngine()
    X = [[0],[5],[10]]
    y = ["a","b","c"]
    r = e.fit(X, y)
    assert r.is_ok() and len(r.value["classes"]) == 3

def test_nb_diagnostics():
    assert OmniNaiveBayesClassifierEngine().diagnostics()["status"] == "operational"

# ═══ TF-IDF ═══
def test_tfidf_basic():
    e = OmniTfIdfVectorizerEngine()
    r = e.fit_transform(["the cat sat", "the dog sat"])
    assert r.is_ok() and r.value["n_documents"] == 2

def test_tfidf_vocab():
    e = OmniTfIdfVectorizerEngine()
    r = e.fit_transform(["hello world"])
    assert r.is_ok() and "hello" in r.value["vocabulary"]

def test_tfidf_cosine():
    e = OmniTfIdfVectorizerEngine()
    r = e.cosine_similarity([1,0,1], [1,0,1])
    assert r.is_ok() and abs(r.value["similarity"] - 1.0) < 1e-6

def test_tfidf_orthogonal():
    e = OmniTfIdfVectorizerEngine()
    r = e.cosine_similarity([1,0], [0,1])
    assert r.is_ok() and abs(r.value["similarity"]) < 1e-6

def test_tfidf_diagnostics():
    assert OmniTfIdfVectorizerEngine().diagnostics()["status"] == "operational"
