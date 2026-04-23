"""Semester 11 Batch 21 — Integration Test Suite (50 tests).

Validates 10 production-grade data science & computational modeling engines:
1. OmniPandasDataframeAggregationEngine
2. OmniNumpyBroadcastingTensorEngine
3. OmniScipyOptimizationSolverEngine
4. OmniScikitlearnRandomForestEngine
5. OmniMatplotlibFigureCanvasEngine
6. OmniStatsmodelsLinearRegressionEngine
7. OmniSeabornStatisticalPlottingEngine
8. OmniBeautifulsoupHtmlParsingEngine
9. OmniSympyAlgebraicExpressionEngine
10. OmniGensimWordEmbeddingEngine
"""
import math
import pytest

# --- Engine Imports ---
from src.compute.python_core.omni_pandas_dataframe_aggregation_engine import OmniPandasDataframeAggregationEngine
from src.compute.python_core.omni_numpy_broadcasting_tensor_engine import OmniNumpyBroadcastingTensorEngine
from src.compute.python_core.omni_scipy_optimization_solver_engine import OmniScipyOptimizationSolverEngine
from src.compute.python_core.omni_scikitlearn_random_forest_engine import OmniScikitlearnRandomForestEngine
from src.compute.python_core.omni_matplotlib_figure_canvas_engine import OmniMatplotlibFigureCanvasEngine
from src.compute.python_core.omni_statsmodels_linear_regression_engine import OmniStatsmodelsLinearRegressionEngine
from src.compute.python_core.omni_seaborn_statistical_plotting_engine import OmniSeabornStatisticalPlottingEngine
from src.compute.python_core.omni_beautifulsoup_html_parsing_engine import OmniBeautifulsoupHtmlParsingEngine
from src.compute.python_core.omni_sympy_algebraic_expression_engine import OmniSympyAlgebraicExpressionEngine
from src.compute.python_core.omni_gensim_word_embedding_engine import OmniGensimWordEmbeddingEngine


# ============================================================
# 1. OmniPandasDataframeAggregationEngine (5 tests)
# ============================================================

def test_pandas_groupby_sum():
    engine = OmniPandasDataframeAggregationEngine()
    rows = [{"city": "NYC", "revenue": 100}, {"city": "LA", "revenue": 200}, {"city": "NYC", "revenue": 50}]
    res = engine.aggregate_groupby(rows, "city", "revenue", ["sum"])
    assert res.is_ok()
    out = res.value
    assert out["groups"]["NYC"]["sum"] == 150.0
    assert out["groups"]["LA"]["sum"] == 200.0
    assert out["total_groups"] == 2

def test_pandas_groupby_mean():
    engine = OmniPandasDataframeAggregationEngine()
    rows = [{"k": "A", "v": 10}, {"k": "A", "v": 20}, {"k": "A", "v": 30}]
    res = engine.aggregate_groupby(rows, "k", "v", ["mean"])
    assert res.is_ok()
    assert res.value["groups"]["A"]["mean"] == 20.0

def test_pandas_groupby_multi_agg():
    engine = OmniPandasDataframeAggregationEngine()
    rows = [{"g": "X", "val": 5}, {"g": "X", "val": 15}, {"g": "Y", "val": 10}]
    res = engine.aggregate_groupby(rows, "g", "val", ["sum", "count", "min", "max"])
    assert res.is_ok()
    x = res.value["groups"]["X"]
    assert x["sum"] == 20.0
    assert x["count"] == 2
    assert x["min"] == 5.0
    assert x["max"] == 15.0

def test_pandas_groupby_empty_error():
    engine = OmniPandasDataframeAggregationEngine()
    res = engine.aggregate_groupby([], "k", "v")
    assert not res.is_ok()

def test_pandas_diagnostics():
    engine = OmniPandasDataframeAggregationEngine()
    diag = engine.diagnostics()
    assert diag["engine"] == "OmniPandasDataframeAggregationEngine"
    assert diag["status"] == "operational"


# ============================================================
# 2. OmniNumpyBroadcastingTensorEngine (5 tests)
# ============================================================

def test_numpy_elementwise_add():
    engine = OmniNumpyBroadcastingTensorEngine()
    res = engine.elementwise_operation([[1, 2], [3, 4]], [[10, 20], [30, 40]], "add")
    assert res.is_ok()
    assert res.value["result_tensor"] == [[11, 22], [33, 44]]

def test_numpy_broadcast_scalar():
    engine = OmniNumpyBroadcastingTensorEngine()
    res = engine.elementwise_operation([[1, 2], [3, 4]], [[10]], "multiply")
    assert res.is_ok()
    assert res.value["result_tensor"] == [[10, 20], [30, 40]]
    assert res.value["broadcast_applied"] is True

def test_numpy_dot_product():
    engine = OmniNumpyBroadcastingTensorEngine()
    res = engine.dot_product([1, 2, 3], [4, 5, 6])
    assert res.is_ok()
    assert res.value["dot_product"] == 32.0

def test_numpy_incompatible_shapes():
    engine = OmniNumpyBroadcastingTensorEngine()
    res = engine.elementwise_operation([[1, 2, 3]], [[1, 2]], "add")
    assert not res.is_ok()

def test_numpy_diagnostics():
    engine = OmniNumpyBroadcastingTensorEngine()
    diag = engine.diagnostics()
    assert diag["engine"] == "OmniNumpyBroadcastingTensorEngine"


# ============================================================
# 3. OmniScipyOptimizationSolverEngine (5 tests)
# ============================================================

def test_scipy_minimize_quadratic():
    engine = OmniScipyOptimizationSolverEngine(max_iterations=500)
    # f(x) = (x-3)² → minimum at x=3
    res = engine.minimize(lambda x: (x[0] - 3) ** 2, [0.0])
    assert res.is_ok()
    assert res.value["converged"] is True
    assert abs(res.value["optimal_point"][0] - 3.0) < 1e-4

def test_scipy_minimize_rosenbrock_2d():
    engine = OmniScipyOptimizationSolverEngine(max_iterations=2000, tolerance=1e-10)
    # Rosenbrock: f(x,y) = (1-x)² + 100(y-x²)² → min at (1,1)
    res = engine.minimize(lambda x: (1 - x[0])**2 + 100*(x[1] - x[0]**2)**2, [0.0, 0.0])
    assert res.is_ok()
    assert abs(res.value["optimal_point"][0] - 1.0) < 0.1
    assert res.value["dimensions"] == 2

def test_scipy_minimize_sphere():
    engine = OmniScipyOptimizationSolverEngine()
    # f(x,y,z) = x²+y²+z² → min at (0,0,0)
    res = engine.minimize(lambda x: sum(xi**2 for xi in x), [5.0, -3.0, 2.0])
    assert res.is_ok()
    for val in res.value["optimal_point"]:
        assert abs(val) < 0.01

def test_scipy_empty_point_error():
    engine = OmniScipyOptimizationSolverEngine()
    res = engine.minimize(lambda x: sum(x), [])
    assert not res.is_ok()

def test_scipy_diagnostics():
    engine = OmniScipyOptimizationSolverEngine()
    diag = engine.diagnostics()
    assert diag["engine"] == "OmniScipyOptimizationSolverEngine"


# ============================================================
# 4. OmniScikitlearnRandomForestEngine (5 tests)
# ============================================================

def test_rf_basic_classification():
    engine = OmniScikitlearnRandomForestEngine(n_trees=5, max_depth=3)
    # Simple linearly separable data
    X_train = [[0, 0], [0, 1], [1, 0], [1, 1]]
    y_train = [0, 0, 1, 1]
    X_test = [[0, 0], [1, 1]]
    res = engine.fit_and_predict(X_train, y_train, X_test)
    assert res.is_ok()
    assert len(res.value["predictions"]) == 2
    assert res.value["n_trees"] == 5

def test_rf_pure_class():
    engine = OmniScikitlearnRandomForestEngine(n_trees=3)
    X_train = [[1], [2], [3]]
    y_train = ["A", "A", "A"]
    X_test = [[4]]
    res = engine.fit_and_predict(X_train, y_train, X_test)
    assert res.is_ok()
    assert res.value["predictions"] == ["A"]

def test_rf_deterministic():
    engine = OmniScikitlearnRandomForestEngine(n_trees=3, random_seed="test-seed")
    X = [[i, i*2] for i in range(10)]
    y = [0]*5 + [1]*5
    r1 = engine.fit_and_predict(X, y, [[5, 10]])
    r2 = engine.fit_and_predict(X, y, [[5, 10]])
    assert r1.is_ok() and r2.is_ok()
    assert r1.value["predictions"] == r2.value["predictions"]

def test_rf_empty_error():
    engine = OmniScikitlearnRandomForestEngine()
    res = engine.fit_and_predict([], [], [[1]])
    assert not res.is_ok()

def test_rf_diagnostics():
    engine = OmniScikitlearnRandomForestEngine()
    diag = engine.diagnostics()
    assert diag["engine"] == "OmniScikitlearnRandomForestEngine"


# ============================================================
# 5. OmniMatplotlibFigureCanvasEngine (5 tests)
# ============================================================

def test_matplotlib_subplot_grid():
    engine = OmniMatplotlibFigureCanvasEngine(dpi=100)
    res = engine.compute_subplot_grid(2, 3, padding=0.05)
    assert res.is_ok()
    assert res.value["total_subplots"] == 6
    assert len(res.value["subplots"]) == 6

def test_matplotlib_dpi_scaling():
    engine = OmniMatplotlibFigureCanvasEngine(dpi=200)
    res = engine.compute_subplot_grid(1, 1, fig_width=5.0, fig_height=4.0)
    assert res.is_ok()
    assert res.value["figure_size_pixels"]["width"] == 1000
    assert res.value["figure_size_pixels"]["height"] == 800

def test_matplotlib_axis_ticks():
    engine = OmniMatplotlibFigureCanvasEngine()
    res = engine.compute_axis_ticks(0, 100, n_ticks=6)
    assert res.is_ok()
    ticks = res.value["ticks"]
    assert len(ticks) >= 2
    assert ticks[0] <= 0

def test_matplotlib_invalid_grid():
    engine = OmniMatplotlibFigureCanvasEngine()
    res = engine.compute_subplot_grid(0, 3)
    assert not res.is_ok()

def test_matplotlib_diagnostics():
    engine = OmniMatplotlibFigureCanvasEngine()
    diag = engine.diagnostics()
    assert diag["engine"] == "OmniMatplotlibFigureCanvasEngine"


# ============================================================
# 6. OmniStatsmodelsLinearRegressionEngine (5 tests)
# ============================================================

def test_ols_simple_fit():
    engine = OmniStatsmodelsLinearRegressionEngine()
    X = [[1], [2], [3], [4], [5]]
    y = [2, 4, 6, 8, 10]  # y = 2x, so intercept=0, slope=2
    res = engine.fit(X, y)
    assert res.is_ok()
    out = res.value
    # intercept ≈ 0, slope ≈ 2
    assert abs(out["coefficients"][1] - 2.0) < 1e-6
    assert out["r_squared"] > 0.999

def test_ols_perfect_fit():
    engine = OmniStatsmodelsLinearRegressionEngine()
    X = [[0], [1], [2]]
    y = [0, 1, 2]
    res = engine.fit(X, y)
    assert res.is_ok()
    assert res.value["r_squared"] > 0.999

def test_ols_multi_feature():
    engine = OmniStatsmodelsLinearRegressionEngine()
    X = [[1, 0], [0, 1], [1, 1], [2, 1]]
    y = [1, 1, 2, 3]  # y ≈ x1 + x2
    res = engine.fit(X, y)
    assert res.is_ok()
    assert res.value["n_parameters"] == 3  # intercept + 2 features

def test_ols_insufficient_samples():
    engine = OmniStatsmodelsLinearRegressionEngine()
    X = [[1, 2]]
    y = [5]
    res = engine.fit(X, y)
    assert not res.is_ok()

def test_ols_diagnostics():
    engine = OmniStatsmodelsLinearRegressionEngine()
    diag = engine.diagnostics()
    assert diag["engine"] == "OmniStatsmodelsLinearRegressionEngine"


# ============================================================
# 7. OmniSeabornStatisticalPlottingEngine (5 tests)
# ============================================================

def test_seaborn_boxplot():
    engine = OmniSeabornStatisticalPlottingEngine()
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    res = engine.compute_box_plot_statistics(data)
    assert res.is_ok()
    out = res.value
    assert out["median"] == 5.5
    assert out["n_data_points"] == 10
    assert out["iqr"] > 0

def test_seaborn_boxplot_outliers():
    engine = OmniSeabornStatisticalPlottingEngine()
    data = [1, 2, 3, 4, 5, 100]  # 100 is outlier
    res = engine.compute_box_plot_statistics(data)
    assert res.is_ok()
    assert 100 in res.value["outliers"]
    assert res.value["n_outliers"] >= 1

def test_seaborn_histogram():
    engine = OmniSeabornStatisticalPlottingEngine()
    data = list(range(100))
    res = engine.compute_histogram_bins(data, n_bins=10)
    assert res.is_ok()
    assert len(res.value["counts"]) == 10
    assert sum(res.value["counts"]) == 100

def test_seaborn_correlation():
    engine = OmniSeabornStatisticalPlottingEngine()
    cols = {"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]}
    res = engine.compute_correlation_matrix(cols)
    assert res.is_ok()
    assert res.value["correlation_matrix"]["x"]["y"] > 0.99

def test_seaborn_diagnostics():
    engine = OmniSeabornStatisticalPlottingEngine()
    diag = engine.diagnostics()
    assert diag["engine"] == "OmniSeabornStatisticalPlottingEngine"


# ============================================================
# 8. OmniBeautifulsoupHtmlParsingEngine (5 tests)
# ============================================================

def test_bs_dom_analysis():
    engine = OmniBeautifulsoupHtmlParsingEngine()
    html = "<html><body><div><p>Hello</p><p>World</p></div></body></html>"
    res = engine.analyze_dom_structure(html)
    assert res.is_ok()
    out = res.value
    assert out["unique_tags"] >= 4
    assert out["max_nesting_depth"] >= 3
    assert out["is_well_formed"] is True

def test_bs_tag_frequency():
    engine = OmniBeautifulsoupHtmlParsingEngine()
    html = "<div><span>A</span><span>B</span><span>C</span></div>"
    res = engine.analyze_dom_structure(html)
    assert res.is_ok()
    assert res.value["tag_frequency"]["span"] == 6  # 3 open + 3 close

def test_bs_attribute_extraction():
    engine = OmniBeautifulsoupHtmlParsingEngine()
    html = '<img src="a.png" alt="A"/><img src="b.png" alt="B"/>'
    res = engine.extract_attributes(html, "img")
    assert res.is_ok()
    assert res.value["instances_found"] == 2
    assert res.value["attributes"][0]["src"] == "a.png"

def test_bs_empty_html_error():
    engine = OmniBeautifulsoupHtmlParsingEngine()
    res = engine.analyze_dom_structure("")
    assert not res.is_ok()

def test_bs_diagnostics():
    engine = OmniBeautifulsoupHtmlParsingEngine()
    diag = engine.diagnostics()
    assert diag["engine"] == "OmniBeautifulsoupHtmlParsingEngine"


# ============================================================
# 9. OmniSympyAlgebraicExpressionEngine (5 tests)
# ============================================================

def test_sympy_polynomial_eval():
    engine = OmniSympyAlgebraicExpressionEngine()
    # p(x) = 1 + 2x + 3x² → p(2) = 1 + 4 + 12 = 17
    res = engine.evaluate_polynomial([1, 2, 3], [0, 1, 2])
    assert res.is_ok()
    assert res.value["y_values"] == [1.0, 6.0, 17.0]

def test_sympy_derivative():
    engine = OmniSympyAlgebraicExpressionEngine()
    # p(x) = 3 + 2x + 5x² → p'(x) = 2 + 10x → coeffs [2, 10]
    res = engine.compute_derivative([3, 2, 5])
    assert res.is_ok()
    assert res.value["derivative_coefficients"] == [2.0, 10.0]

def test_sympy_quadratic_real_roots():
    engine = OmniSympyAlgebraicExpressionEngine()
    # x² - 5x + 6 = 0 → roots 2, 3
    res = engine.find_roots_quadratic(1, -5, 6)
    assert res.is_ok()
    roots = sorted(res.value["roots"])
    assert abs(roots[0] - 2.0) < 1e-10
    assert abs(roots[1] - 3.0) < 1e-10

def test_sympy_quadratic_complex():
    engine = OmniSympyAlgebraicExpressionEngine()
    # x² + 1 = 0 → complex roots
    res = engine.find_roots_quadratic(1, 0, 1)
    assert res.is_ok()
    assert res.value["root_type"] == "complex_conjugate"

def test_sympy_diagnostics():
    engine = OmniSympyAlgebraicExpressionEngine()
    diag = engine.diagnostics()
    assert diag["engine"] == "OmniSympyAlgebraicExpressionEngine"


# ============================================================
# 10. OmniGensimWordEmbeddingEngine (5 tests)
# ============================================================

def test_gensim_cosine_similarity():
    engine = OmniGensimWordEmbeddingEngine()
    res = engine.cosine_similarity([1, 0, 0], [1, 0, 0])
    assert res.is_ok()
    assert res.value["cosine_similarity"] == 1.0

def test_gensim_cosine_orthogonal():
    engine = OmniGensimWordEmbeddingEngine()
    res = engine.cosine_similarity([1, 0], [0, 1])
    assert res.is_ok()
    assert res.value["cosine_similarity"] == 0.0

def test_gensim_most_similar():
    engine = OmniGensimWordEmbeddingEngine()
    vocab = {"king": [1.0, 0.5], "queen": [0.9, 0.6], "car": [-1.0, 0.0]}
    res = engine.find_most_similar([1.0, 0.5], vocab, top_k=2)
    assert res.is_ok()
    assert res.value["most_similar"][0]["word"] == "king"

def test_gensim_tfidf():
    engine = OmniGensimWordEmbeddingEngine()
    docs = [["the", "cat", "sat"], ["the", "dog", "ran"], ["cat", "dog", "played"]]
    res = engine.compute_tfidf_weights(docs)
    assert res.is_ok()
    assert res.value["n_documents"] == 3
    assert res.value["vocabulary_size"] >= 5

def test_gensim_diagnostics():
    engine = OmniGensimWordEmbeddingEngine()
    diag = engine.diagnostics()
    assert diag["engine"] == "OmniGensimWordEmbeddingEngine"
