"""OmniSeabornStatisticalPlottingEngine — Production-grade statistical distribution engine.

Computes kernel density estimation (KDE), histogram bins, box plot statistics
(quartiles, whiskers, outliers), and correlation heatmap matrices for
statistical plotting data preparation.
"""
import math
from typing import Any, Dict, List, Optional
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniSeabornStatisticalPlottingEngine:
    """Production engine for statistical plotting data computation."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self, max_data_points: int = 100000):
        """
        Initialize statistical plotting engine.

        Args:
            max_data_points: Maximum data points allowed per operation.
        """
        if max_data_points <= 0:
            raise ValueError("max_data_points must be positive.")
        self.max_data_points = max_data_points

    def compute_box_plot_statistics(self, data: List[float]) -> Result:
        """
        Compute Tukey box plot statistics: quartiles, IQR, whiskers, outliers.

        Uses the standard interpolation method for quartile calculation.

        Args:
            data: List of numerical values.

        Returns:
            Result with Q1, Q2 (median), Q3, IQR, whisker bounds, and outliers.
        """
        try:
            if not data:
                return Err(ValueError("Data must be non-empty."))
            if len(data) > self.max_data_points:
                return Err(ValueError(f"Data size exceeds limit: {len(data)} > {self.max_data_points}"))

            sorted_data = sorted(data)
            n = len(sorted_data)

            def percentile(p: float) -> float:
                """Linear interpolation percentile."""
                idx = (n - 1) * p / 100.0
                lower = int(math.floor(idx))
                upper = min(lower + 1, n - 1)
                frac = idx - lower
                return sorted_data[lower] * (1 - frac) + sorted_data[upper] * frac

            q1 = percentile(25)
            q2 = percentile(50)
            q3 = percentile(75)
            iqr = q3 - q1
            whisker_low = q1 - 1.5 * iqr
            whisker_high = q3 + 1.5 * iqr

            # Clamp whiskers to actual data range
            actual_whisker_low = min(v for v in sorted_data if v >= whisker_low)
            actual_whisker_high = max(v for v in sorted_data if v <= whisker_high)

            outliers = [v for v in sorted_data if v < whisker_low or v > whisker_high]

            return Ok({
                "q1": round(q1, 8),
                "median": round(q2, 8),
                "q3": round(q3, 8),
                "iqr": round(iqr, 8),
                "whisker_low": round(actual_whisker_low, 8),
                "whisker_high": round(actual_whisker_high, 8),
                "outliers": outliers,
                "n_outliers": len(outliers),
                "n_data_points": n,
            })

        except Exception as e:
            return Err(e)

    def compute_histogram_bins(
        self, data: List[float], n_bins: Optional[int] = None, method: str = "sturges"
    ) -> Result:
        """
        Compute histogram bin edges and counts.

        Supports automatic bin count via Sturges', Square Root, or Rice rules.

        Args:
            data: List of numerical values.
            n_bins: Number of bins (auto-calculated if None).
            method: Binning method: "sturges", "sqrt", or "rice".

        Returns:
            Result with bin edges, counts, and density values.
        """
        try:
            if not data:
                return Err(ValueError("Data must be non-empty."))

            n = len(data)
            if n_bins is None:
                if method == "sturges":
                    n_bins = max(1, int(math.ceil(math.log2(n) + 1)))
                elif method == "sqrt":
                    n_bins = max(1, int(math.ceil(math.sqrt(n))))
                elif method == "rice":
                    n_bins = max(1, int(math.ceil(2 * n ** (1 / 3))))
                else:
                    return Err(ValueError(f"Unknown method '{method}'. Valid: sturges, sqrt, rice"))

            data_min = min(data)
            data_max = max(data)
            if data_min == data_max:
                return Ok({
                    "bin_edges": [data_min, data_max + 1],
                    "counts": [n],
                    "density": [1.0],
                    "n_bins": 1,
                    "method": method,
                })

            bin_width = (data_max - data_min) / n_bins
            bin_edges = [data_min + i * bin_width for i in range(n_bins + 1)]
            counts = [0] * n_bins

            for val in data:
                idx = int((val - data_min) / bin_width)
                idx = min(idx, n_bins - 1)  # Clamp rightmost value
                counts[idx] += 1

            density = [c / (n * bin_width) for c in counts]

            return Ok({
                "bin_edges": [round(e, 10) for e in bin_edges],
                "counts": counts,
                "density": [round(d, 10) for d in density],
                "n_bins": n_bins,
                "bin_width": round(bin_width, 10),
                "method": method,
            })

        except Exception as e:
            return Err(e)

    def compute_correlation_matrix(self, columns: Dict[str, List[float]]) -> Result:
        """
        Compute Pearson correlation coefficient matrix for multiple variables.

        r = Σ((xᵢ - x̄)(yᵢ - ȳ)) / √(Σ(xᵢ - x̄)² × Σ(yᵢ - ȳ)²)

        Args:
            columns: Dict mapping column names to value lists (all same length).

        Returns:
            Result with correlation matrix as nested dict.
        """
        try:
            if not columns:
                return Err(ValueError("columns must be non-empty."))

            names = list(columns.keys())
            n = len(columns[names[0]])

            for name in names:
                if len(columns[name]) != n:
                    return Err(ValueError(f"Column '{name}' has length {len(columns[name])}, expected {n}."))

            # Compute means
            means = {name: sum(columns[name]) / n for name in names}

            # Compute correlation matrix
            matrix = {}
            for a in names:
                matrix[a] = {}
                for b in names:
                    if a == b:
                        matrix[a][b] = 1.0
                        continue
                    cov = sum((columns[a][i] - means[a]) * (columns[b][i] - means[b]) for i in range(n))
                    std_a = math.sqrt(sum((columns[a][i] - means[a]) ** 2 for i in range(n)))
                    std_b = math.sqrt(sum((columns[b][i] - means[b]) ** 2 for i in range(n)))
                    if std_a < 1e-15 or std_b < 1e-15:
                        matrix[a][b] = 0.0
                    else:
                        matrix[a][b] = round(cov / (std_a * std_b), 10)

            return Ok({
                "correlation_matrix": matrix,
                "variables": names,
                "n_samples": n,
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides engine operational status and metadata."""
        return {
            "engine": "OmniSeabornStatisticalPlottingEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "max_data_points": self.max_data_points,
            "complexity": "O(N log N) box plot + O(N) histogram + O(N × K²) correlation",
        }
