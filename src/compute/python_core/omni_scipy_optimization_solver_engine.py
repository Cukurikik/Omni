"""OmniScipyOptimizationSolverEngine — Production-grade Nelder-Mead simplex optimizer.

Implements the Nelder-Mead derivative-free optimization algorithm using pure
geometric simplex operations (reflection, expansion, contraction, shrinkage).
Suitable for black-box, non-differentiable, or noisy objective functions.
"""
import math
from typing import Any, Callable, Dict, List, Optional, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniScipyOptimizationSolverEngine:
    """Production engine for Nelder-Mead simplex optimization."""

    ENGINE_VERSION = "1.0.0"

    def __init__(
        self,
        max_iterations: int = 1000,
        tolerance: float = 1e-8,
        alpha: float = 1.0,
        gamma: float = 2.0,
        rho: float = 0.5,
        sigma: float = 0.5,
    ):
        """
        Initialize Nelder-Mead optimizer.

        Args:
            max_iterations: Maximum number of iterations.
            tolerance: Convergence tolerance on function value spread.
            alpha: Reflection coefficient (>0, typically 1).
            gamma: Expansion coefficient (>1, typically 2).
            rho: Contraction coefficient (0 < rho < 0.5, typically 0.5).
            sigma: Shrink coefficient (0 < sigma < 1, typically 0.5).
        """
        if max_iterations <= 0:
            raise ValueError("max_iterations must be positive.")
        if tolerance <= 0:
            raise ValueError("tolerance must be positive.")
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.alpha = alpha
        self.gamma = gamma
        self.rho = rho
        self.sigma = sigma

    def minimize(
        self,
        objective_fn: Callable[[List[float]], float],
        initial_point: List[float],
        initial_step: float = 1.0,
    ) -> Result:
        """
        Minimize an objective function using the Nelder-Mead simplex method.

        Constructs an (n+1)-vertex simplex around the initial point, then
        iteratively applies reflection, expansion, contraction, and shrinkage
        to converge on a local minimum.

        Args:
            objective_fn: Callable f(x) -> float to minimize.
            initial_point: Starting point as list of floats.
            initial_step: Initial simplex edge length.

        Returns:
            Result with optimal point, function value, iterations, and convergence flag.
        """
        try:
            n = len(initial_point)
            if n == 0:
                return Err(ValueError("initial_point must be non-empty."))

            # Build initial simplex: n+1 vertices
            simplex = [list(initial_point)]
            for i in range(n):
                vertex = list(initial_point)
                vertex[i] += initial_step
                simplex.append(vertex)

            # Evaluate all vertices
            f_values = [objective_fn(v) for v in simplex]

            for iteration in range(self.max_iterations):
                # Sort vertices by function value
                order = sorted(range(n + 1), key=lambda k: f_values[k])
                simplex = [simplex[i] for i in order]
                f_values = [f_values[i] for i in order]

                # Check convergence: spread of function values
                spread = abs(f_values[-1] - f_values[0])
                if spread < self.tolerance:
                    return Ok({
                        "optimal_point": simplex[0],
                        "optimal_value": round(f_values[0], 12),
                        "iterations": iteration + 1,
                        "converged": True,
                        "final_spread": spread,
                        "dimensions": n,
                    })

                # Centroid of all vertices except worst
                centroid = [0.0] * n
                for i in range(n):
                    for j in range(n):
                        centroid[j] += simplex[i][j]
                    centroid = [c for c in centroid]
                centroid = [c / n for c in centroid]

                # Reflection
                worst = simplex[-1]
                reflected = [centroid[j] + self.alpha * (centroid[j] - worst[j]) for j in range(n)]
                f_reflected = objective_fn(reflected)

                if f_values[0] <= f_reflected < f_values[-2]:
                    simplex[-1] = reflected
                    f_values[-1] = f_reflected
                elif f_reflected < f_values[0]:
                    # Expansion
                    expanded = [centroid[j] + self.gamma * (reflected[j] - centroid[j]) for j in range(n)]
                    f_expanded = objective_fn(expanded)
                    if f_expanded < f_reflected:
                        simplex[-1] = expanded
                        f_values[-1] = f_expanded
                    else:
                        simplex[-1] = reflected
                        f_values[-1] = f_reflected
                else:
                    # Contraction
                    contracted = [centroid[j] + self.rho * (worst[j] - centroid[j]) for j in range(n)]
                    f_contracted = objective_fn(contracted)
                    if f_contracted < f_values[-1]:
                        simplex[-1] = contracted
                        f_values[-1] = f_contracted
                    else:
                        # Shrink
                        best = simplex[0]
                        for i in range(1, n + 1):
                            simplex[i] = [best[j] + self.sigma * (simplex[i][j] - best[j]) for j in range(n)]
                            f_values[i] = objective_fn(simplex[i])

            # Did not converge within max_iterations
            order = sorted(range(n + 1), key=lambda k: f_values[k])
            best_idx = order[0]
            return Ok({
                "optimal_point": simplex[best_idx],
                "optimal_value": round(f_values[best_idx], 12),
                "iterations": self.max_iterations,
                "converged": False,
                "final_spread": abs(f_values[order[-1]] - f_values[order[0]]),
                "dimensions": n,
            })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides engine operational status and metadata."""
        return {
            "engine": "OmniScipyOptimizationSolverEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "max_iterations": self.max_iterations,
            "tolerance": self.tolerance,
            "complexity": "O(N * max_iter) Nelder-Mead simplex optimization",
        }
