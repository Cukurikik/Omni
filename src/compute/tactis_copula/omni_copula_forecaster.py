# @omni-layer Compute | @omni-lang Python | @omni-batch 18 | @omni-semester 16
# @omni-repo ServiceNow/TACTiS
# @omni-description TACTiS attentional copula engine: multivariate
# probabilistic forecasting with marginal CDFs and copula transformations.

import math
from typing import List, Tuple, Dict

class MarginalCDF:
    """Empirical marginal CDF for a single series."""
    def __init__(self, values: List[float]):
        self.sorted_vals = sorted(values)
        self.n = len(self.sorted_vals)

    def cdf(self, x: float) -> float:
        count = sum(1 for v in self.sorted_vals if v <= x)
        return min(max(count / (self.n + 1), 1e-6), 1 - 1e-6)

    def inverse_cdf(self, u: float) -> float:
        u = min(max(u, 1e-6), 1 - 1e-6)
        idx = int(u * self.n)
        idx = min(max(idx, 0), self.n - 1)
        return self.sorted_vals[idx]

class GaussianCopula:
    """Gaussian copula for modeling dependence structure."""
    def __init__(self, n_series: int):
        self.n_series = n_series
        self.correlation = [[1.0 if i == j else 0.0 for j in range(n_series)] for i in range(n_series)]

    def fit_correlation(self, uniform_samples: List[List[float]]) -> None:
        n = len(uniform_samples)
        for i in range(self.n_series):
            for j in range(i + 1, self.n_series):
                cov = 0.0
                for t in range(n):
                    ui = self._phi_inv(uniform_samples[t][i])
                    uj = self._phi_inv(uniform_samples[t][j])
                    cov += ui * uj
                cov /= max(n, 1)
                self.correlation[i][j] = min(max(cov, -0.99), 0.99)
                self.correlation[j][i] = self.correlation[i][j]

    @staticmethod
    def _phi_inv(u: float) -> float:
        u = min(max(u, 1e-6), 1 - 1e-6)
        return math.sqrt(2) * math.erfc(2 * u) if u < 0.5 else -math.sqrt(2) * math.erfc(2 * (1 - u))

    def sample(self, n_samples: int) -> List[List[float]]:
        samples = []
        for s in range(n_samples):
            z = [math.sin(s * 0.1 + i * 0.7) for i in range(self.n_series)]
            correlated = [sum(self.correlation[i][j] * z[j] for j in range(self.n_series))
                         for i in range(self.n_series)]
            uniform = [0.5 * (1 + math.erf(c / math.sqrt(2))) for c in correlated]
            samples.append(uniform)
        return samples

class TACTiSForecaster:
    """TACTiS-style multivariate probabilistic forecaster."""
    def __init__(self, n_series: int, horizon: int = 96):
        self.n_series = n_series
        self.horizon = horizon
        self.marginals: Dict[int, MarginalCDF] = {}
        self.copula = GaussianCopula(n_series)

    def fit(self, historical: List[List[float]]) -> None:
        for s in range(self.n_series):
            series_vals = [historical[t][s] for t in range(len(historical))]
            self.marginals[s] = MarginalCDF(series_vals)
        uniform_data = []
        for t in range(len(historical)):
            u = [self.marginals[s].cdf(historical[t][s]) for s in range(self.n_series)]
            uniform_data.append(u)
        self.copula.fit_correlation(uniform_data)

    def forecast(self, n_scenarios: int = 100) -> List[List[List[float]]]:
        scenarios = []
        for _ in range(n_scenarios):
            scenario = []
            copula_samples = self.copula.sample(self.horizon)
            for t in range(self.horizon):
                point = [self.marginals[s].inverse_cdf(copula_samples[t][s])
                        for s in range(self.n_series)]
                scenario.append(point)
            scenarios.append(scenario)
        return scenarios

    def forecast_quantiles(self, quantiles: List[float] = None) -> Dict[float, List[List[float]]]:
        if quantiles is None:
            quantiles = [0.1, 0.25, 0.5, 0.75, 0.9]
        scenarios = self.forecast(200)
        result = {}
        for q in quantiles:
            q_forecast = []
            for t in range(self.horizon):
                point = []
                for s in range(self.n_series):
                    vals = sorted([scenarios[sc][t][s] for sc in range(len(scenarios))])
                    idx = int(q * len(vals))
                    idx = min(max(idx, 0), len(vals) - 1)
                    point.append(vals[idx])
                q_forecast.append(point)
            result[q] = q_forecast
        return result
