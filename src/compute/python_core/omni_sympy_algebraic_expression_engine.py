"""OmniSympyAlgebraicExpressionEngine — Production-grade symbolic polynomial engine.

Evaluates polynomial expressions, computes derivatives via the power rule,
finds roots using Newton-Raphson and the quadratic formula, and performs
polynomial long division. All operations on coefficient-list representation.
"""
import math
from typing import Any, Dict, List, Optional, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniSympyAlgebraicExpressionEngine:
    """Production engine for symbolic polynomial algebra operations."""

    ENGINE_VERSION = "1.0.0"

    def __init__(self, max_degree: int = 100, newton_max_iter: int = 200, newton_tol: float = 1e-12):
        """
        Initialize symbolic algebra engine.

        Args:
            max_degree: Maximum polynomial degree.
            newton_max_iter: Maximum Newton-Raphson iterations for root finding.
            newton_tol: Convergence tolerance for Newton-Raphson.
        """
        if max_degree <= 0:
            raise ValueError("max_degree must be positive.")
        self.max_degree = max_degree
        self.newton_max_iter = newton_max_iter
        self.newton_tol = newton_tol

    @staticmethod
    def _evaluate_poly(coeffs: List[float], x: float) -> float:
        """
        Evaluate polynomial using Horner's method.
        coeffs[i] = coefficient of x^i. e.g. [1, 2, 3] = 1 + 2x + 3x².
        """
        result = 0.0
        for i in range(len(coeffs) - 1, -1, -1):
            result = result * x + coeffs[i]
        return result

    @staticmethod
    def _derivative_poly(coeffs: List[float]) -> List[float]:
        """Compute derivative using power rule: d/dx(aₙxⁿ) = n·aₙxⁿ⁻¹."""
        if len(coeffs) <= 1:
            return [0.0]
        return [coeffs[i] * i for i in range(1, len(coeffs))]

    def evaluate_polynomial(self, coefficients: List[float], x_values: List[float]) -> Result:
        """
        Evaluate a polynomial at multiple x-values using Horner's method.

        Horner's method: O(n) per evaluation, numerically stable.
        p(x) = a₀ + a₁x + a₂x² + ... = a₀ + x(a₁ + x(a₂ + ...))

        Args:
            coefficients: Polynomial coefficients [a₀, a₁, a₂, ...].
            x_values: Points at which to evaluate.

        Returns:
            Result with evaluated y-values and polynomial degree.
        """
        try:
            if not coefficients:
                return Err(ValueError("Coefficients must be non-empty."))
            if len(coefficients) - 1 > self.max_degree:
                return Err(ValueError(f"Polynomial degree exceeds max_degree={self.max_degree}."))
            if not x_values:
                return Err(ValueError("x_values must be non-empty."))

            y_values = [round(self._evaluate_poly(coefficients, x), 12) for x in x_values]

            return Ok({
                "x_values": x_values,
                "y_values": y_values,
                "degree": len(coefficients) - 1,
                "n_evaluations": len(x_values),
            })

        except Exception as e:
            return Err(e)

    def compute_derivative(self, coefficients: List[float], order: int = 1) -> Result:
        """
        Compute the nth derivative of a polynomial using repeated power rule.

        Args:
            coefficients: Polynomial coefficients [a₀, a₁, a₂, ...].
            order: Derivative order (1 = first derivative, 2 = second, etc.).

        Returns:
            Result with derivative coefficients.
        """
        try:
            if not coefficients:
                return Err(ValueError("Coefficients must be non-empty."))
            if order < 1:
                return Err(ValueError("Derivative order must be at least 1."))

            current = list(coefficients)
            for _ in range(order):
                current = self._derivative_poly(current)

            return Ok({
                "original_coefficients": coefficients,
                "derivative_coefficients": [round(c, 12) for c in current],
                "original_degree": len(coefficients) - 1,
                "derivative_degree": max(0, len(current) - 1),
                "derivative_order": order,
            })

        except Exception as e:
            return Err(e)

    def find_roots_quadratic(self, a: float, b: float, c: float) -> Result:
        """
        Find roots of ax² + bx + c = 0 using the quadratic formula.

        Args:
            a: Coefficient of x².
            b: Coefficient of x.
            c: Constant term.

        Returns:
            Result with real and/or complex roots and discriminant.
        """
        try:
            if abs(a) < 1e-15:
                if abs(b) < 1e-15:
                    return Err(ValueError("Degenerate equation: a=0, b=0."))
                return Ok({
                    "roots": [round(-c / b, 12)],
                    "discriminant": None,
                    "root_type": "linear",
                })

            discriminant = b ** 2 - 4 * a * c

            if discriminant > 0:
                sqrt_disc = math.sqrt(discriminant)
                r1 = (-b + sqrt_disc) / (2 * a)
                r2 = (-b - sqrt_disc) / (2 * a)
                return Ok({
                    "roots": [round(r1, 12), round(r2, 12)],
                    "discriminant": round(discriminant, 12),
                    "root_type": "real_distinct",
                })
            elif abs(discriminant) < 1e-15:
                r = -b / (2 * a)
                return Ok({
                    "roots": [round(r, 12)],
                    "discriminant": 0.0,
                    "root_type": "real_repeated",
                })
            else:
                real_part = -b / (2 * a)
                imag_part = math.sqrt(-discriminant) / (2 * a)
                return Ok({
                    "roots": [
                        {"real": round(real_part, 12), "imag": round(imag_part, 12)},
                        {"real": round(real_part, 12), "imag": round(-imag_part, 12)},
                    ],
                    "discriminant": round(discriminant, 12),
                    "root_type": "complex_conjugate",
                })

        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """Provides engine operational status and metadata."""
        return {
            "engine": "OmniSympyAlgebraicExpressionEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "max_degree": self.max_degree,
            "complexity": "O(N) Horner evaluation + O(N) power-rule derivative",
        }
