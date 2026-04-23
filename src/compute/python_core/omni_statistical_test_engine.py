"""OmniStatisticalTestEngine — Production-grade statistical hypothesis testing.

Implements z-test, t-test, chi-squared test, and Pearson correlation
using pure mathematical formulas. No external dependencies.
"""
import math
from typing import Any, Dict, List
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniStatisticalTestEngine:
    """Production engine for statistical hypothesis testing."""

    ENGINE_VERSION = "1.0.0"

    @staticmethod
    def _mean(data):
        return sum(data) / len(data)

    @staticmethod
    def _var(data, ddof=1):
        m = sum(data) / len(data)
        return sum((x - m) ** 2 for x in data) / (len(data) - ddof)

    def z_test(self, sample: List[float], pop_mean: float, pop_std: float) -> Result:
        """Perform z test computation.

            Args:
                    sample: List[float]
                    pop_mean: float
                    pop_std: float

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            n = len(sample)
            if n == 0:
                return Err(ValueError("Sample must be non-empty."))
            sample_mean = self._mean(sample)
            z = (sample_mean - pop_mean) / (pop_std / math.sqrt(n))
            return Ok({"z_statistic": round(z, 10), "sample_mean": round(sample_mean, 10),
                        "pop_mean": pop_mean, "n": n})
        except Exception as e:
            return Err(e)

    def t_test_one_sample(self, sample: List[float], mu: float) -> Result:
        """Perform t test one sample computation.

            Args:
                    sample: List[float]
                    mu: float

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            n = len(sample)
            if n < 2:
                return Err(ValueError("Need at least 2 samples."))
            m = self._mean(sample)
            s = math.sqrt(self._var(sample))
            t = (m - mu) / (s / math.sqrt(n))
            df = n - 1
            return Ok({"t_statistic": round(t, 10), "degrees_of_freedom": df,
                        "sample_mean": round(m, 10), "sample_std": round(s, 10), "n": n})
        except Exception as e:
            return Err(e)

    def t_test_two_sample(self, a: List[float], b: List[float]) -> Result:
        """Perform t test two sample computation.

            Args:
                    a: List[float]
                    b: List[float]

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            na, nb = len(a), len(b)
            if na < 2 or nb < 2:
                return Err(ValueError("Need at least 2 samples in each group."))
            ma, mb = self._mean(a), self._mean(b)
            va, vb = self._var(a), self._var(b)
            se = math.sqrt(va / na + vb / nb)
            t = (ma - mb) / se
            df_num = (va / na + vb / nb) ** 2
            df_den = (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)
            df = df_num / df_den if df_den > 0 else na + nb - 2
            return Ok({"t_statistic": round(t, 10), "degrees_of_freedom": round(df, 4),
                        "mean_a": round(ma, 10), "mean_b": round(mb, 10)})
        except Exception as e:
            return Err(e)

    def pearson_correlation(self, x: List[float], y: List[float]) -> Result:
        """Perform pearson correlation computation.

            Args:
                    x: List[float]
                    y: List[float]

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            n = len(x)
            if n != len(y) or n < 2:
                return Err(ValueError("x and y must be same length and ≥ 2."))
            mx, my = self._mean(x), self._mean(y)
            cov = sum((x[i] - mx) * (y[i] - my) for i in range(n)) / (n - 1)
            sx = math.sqrt(self._var(x))
            sy = math.sqrt(self._var(y))
            if sx == 0 or sy == 0:
                return Ok({"r": 0.0, "r_squared": 0.0, "n": n})
            r = cov / (sx * sy)
            return Ok({"r": round(r, 10), "r_squared": round(r * r, 10), "n": n,
                        "covariance": round(cov, 10)})
        except Exception as e:
            return Err(e)

    def chi_squared(self, observed: List[float], expected: List[float]) -> Result:
        """Perform chi squared computation.

            Args:
                    observed: List[float]
                    expected: List[float]

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        try:
            if len(observed) != len(expected):
                return Err(ValueError("Observed and expected must be same length."))
            chi2 = sum((o - e) ** 2 / e for o, e in zip(observed, expected) if e > 0)
            df = len(observed) - 1
            return Ok({"chi_squared": round(chi2, 10), "degrees_of_freedom": df, "k": len(observed)})
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        return {"engine": "OmniStatisticalTestEngine", "version": self.ENGINE_VERSION,
                "status": "operational", "tests": ["z-test", "t-test", "chi-squared", "Pearson correlation"]}
