"""
OMNI DeepXDE Engine — Physics-informed neural network primitives for solving PDEs.
Assimilated from: lululxvi/deepxde
Provides: Finite difference gradients, PDE residual evaluation, collocation point sampling, boundary loss.
"""
import numpy as np
from typing import Callable, Optional, Tuple



ENGINE_VERSION = "1.0.0-omni"

class Result:
    """Monadic Result base."""
    pass


class Ok(Result):
    """Success variant."""
    def __init__(self, value):
        """Initialize Ok."""
        self.value = value


class Err(Result):
    """Error variant."""
    def __init__(self, error: str):
        """Initialize Err."""
        self.error = error


class OmniDeepXDEEngine:
    """
    Pure NumPy physics-informed computation engine inspired by DeepXDE.

    Implements the mathematical foundation of PINNs (Physics-Informed Neural Networks):
      - Finite difference approximations for spatial derivatives
      - PDE residual computation for arbitrary governing equations
      - Collocation point sampling (uniform, Latin Hypercube)
      - Boundary condition loss evaluation

    @since 1.0.0
    @tags ["pinn", "pde", "physics-informed", "scientific-computing", "compute"]
    """

    def __init__(self) -> None:
        """Initialize OmniDeepXDEEngine."""
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    def diagnostics(self) -> Result:
        """Returns engine health status."""
        return Ok({"status": "active", "engine": "DeepXDE", "capability": "PhysicsInformedNeuralNetworks"})

    def finite_diff_gradient(self, f_values: np.ndarray, dx: float, order: int = 1) -> Result:
        """
        Computes the spatial derivative of f using central finite differences.

        1st order: f'(x) ≈ (f(x+dx) - f(x-dx)) / (2*dx)
        2nd order: f''(x) ≈ (f(x+dx) - 2*f(x) + f(x-dx)) / dx^2

        @param f_values: 1D array of function values on a uniform grid.
        @param dx: Grid spacing.
        @param order: Derivative order (1 or 2).
        @returns Result containing 1D array of derivative values (interior points only).
        """
        if f_values.ndim != 1:
            return Err("f_values must be a 1D array.")
        if dx <= 0:
            return Err("dx must be positive.")
        if len(f_values) < 3:
            return Err("Need at least 3 points for finite differences.")

        if order == 1:
            deriv = (f_values[2:] - f_values[:-2]) / (2.0 * dx)
        elif order == 2:
            deriv = (f_values[2:] - 2.0 * f_values[1:-1] + f_values[:-2]) / (dx ** 2)
        else:
            return Err("Only order 1 and 2 derivatives are supported.")

        return Ok(deriv)

    def finite_diff_gradient_2d(
        self,
        f_grid: np.ndarray,
        dx: float,
        dy: float,
        deriv_x: int = 0,
        deriv_y: int = 0,
    ) -> Result:
        """
        Computes partial derivatives on a 2D grid using central finite differences.

        @param f_grid: 2D array of function values, shape (Ny, Nx).
        @param dx: Grid spacing in x direction.
        @param dy: Grid spacing in y direction.
        @param deriv_x: Derivative order in x (0, 1, or 2).
        @param deriv_y: Derivative order in y (0, 1, or 2).
        @returns Result containing 2D array of derivative values (interior region).
        """
        if f_grid.ndim != 2:
            return Err("f_grid must be 2D.")

        result = f_grid.copy()

        # Apply x-derivatives
        if deriv_x == 1:
            result = (result[:, 2:] - result[:, :-2]) / (2.0 * dx)
        elif deriv_x == 2:
            result = (result[:, 2:] - 2.0 * result[:, 1:-1] + result[:, :-2]) / (dx ** 2)
        elif deriv_x != 0:
            return Err("deriv_x must be 0, 1, or 2.")

        # Apply y-derivatives
        if deriv_y == 1:
            result = (result[2:, :] - result[:-2, :]) / (2.0 * dy)
        elif deriv_y == 2:
            result = (result[2:, :] - 2.0 * result[1:-1, :] + result[:-2, :]) / (dy ** 2)
        elif deriv_y != 0:
            return Err("deriv_y must be 0, 1, or 2.")

        return Ok(result)

    def sample_collocation_uniform(
        self,
        bounds: np.ndarray,
        n_points: int,
    ) -> Result:
        """
        Samples collocation points uniformly within a hypercube domain.

        @param bounds: (ndim, 2) array where bounds[i] = [lower_i, upper_i].
        @param n_points: Number of points to sample.
        @returns Result containing (n_points, ndim) array of collocation points.
        """
        if bounds.ndim != 2 or bounds.shape[1] != 2:
            return Err("Bounds must be (ndim, 2) array with [lower, upper] per dimension.")
        if n_points <= 0:
            return Err("n_points must be positive.")

        ndim = bounds.shape[0]
        lowers = bounds[:, 0]
        uppers = bounds[:, 1]

        points = np.random.rand(n_points, ndim) * (uppers - lowers) + lowers
        return Ok(points)

    def sample_collocation_lhs(self, bounds: np.ndarray, n_points: int) -> Result:
        """
        Latin Hypercube Sampling (LHS) for stratified collocation point generation.
        Produces better space coverage than uniform random sampling.

        @param bounds: (ndim, 2) array with [lower, upper] per dimension.
        @param n_points: Number of samples.
        @returns Result containing (n_points, ndim) LHS samples.
        """
        if bounds.ndim != 2 or bounds.shape[1] != 2:
            return Err("Bounds must be (ndim, 2).")
        if n_points <= 0:
            return Err("n_points must be positive.")

        ndim = bounds.shape[0]
        samples = np.zeros((n_points, ndim), dtype=np.float64)

        for d in range(ndim):
            # Create stratified bins
            perm = np.random.permutation(n_points)
            lower = bounds[d, 0]
            upper = bounds[d, 1]
            bin_width = (upper - lower) / n_points

            for i in range(n_points):
                bin_idx = perm[i]
                samples[i, d] = lower + bin_width * (bin_idx + np.random.rand())

        return Ok(samples)

    def compute_pde_residual_poisson(
        self,
        u_grid: np.ndarray,
        f_grid: np.ndarray,
        dx: float,
        dy: float,
    ) -> Result:
        """
        Computes the residual of the 2D Poisson equation:

            r = ∇²u - f = (d²u/dx² + d²u/dy²) - f

        A zero residual implies the PDE is satisfied exactly.

        @param u_grid: 2D grid of the solution u(x, y), shape (Ny, Nx).
        @param f_grid: 2D grid of the source term f(x, y), same shape as u.
        @param dx: Grid spacing in x.
        @param dy: Grid spacing in y.
        @returns Result containing 2D residual array (interior region only).
        """
        if u_grid.shape != f_grid.shape:
            return Err("u_grid and f_grid must have the same shape.")

        # Compute Laplacian via central differences
        laplacian_x = (u_grid[:, 2:] - 2.0 * u_grid[:, 1:-1] + u_grid[:, :-2]) / (dx ** 2)
        laplacian_y = (u_grid[2:, :] - 2.0 * u_grid[1:-1, :] + u_grid[:-2, :]) / (dy ** 2)

        # Both reduce the grid; take the common interior
        laplacian = laplacian_x[1:-1, :] + laplacian_y[:, 1:-1]
        f_interior = f_grid[1:-1, 1:-1]

        residual = laplacian - f_interior
        return Ok(residual)

    def boundary_loss_dirichlet(
        self,
        u_boundary: np.ndarray,
        target_values: np.ndarray,
    ) -> Result:
        """
        Computes the Dirichlet boundary condition loss.

        L_bc = (1/N) * sum((u_boundary - target)^2)

        @param u_boundary: 1D array of solution values at boundary points.
        @param target_values: 1D array of prescribed boundary values.
        @returns Result containing scalar MSE loss.
        """
        if u_boundary.shape != target_values.shape:
            return Err("u_boundary and target_values must have the same shape.")

        mse = float(np.mean((u_boundary - target_values) ** 2))
        return Ok(mse)

    def compute_total_pinn_loss(
        self,
        pde_residual: np.ndarray,
        bc_loss: float,
        lambda_bc: float = 1.0,
    ) -> Result:
        """
        Computes the total PINN loss combining PDE residual and boundary condition terms.

        L_total = MSE(residual) + lambda_bc * L_bc

        @param pde_residual: Array of PDE residual values at collocation points.
        @param bc_loss: Scalar boundary condition loss.
        @param lambda_bc: Relative weight for the boundary loss (default 1.0).
        @returns Result containing scalar total loss.
        """
        pde_loss = float(np.mean(pde_residual ** 2))
        total = pde_loss + lambda_bc * bc_loss
        return Ok({"total_loss": total, "pde_loss": pde_loss, "bc_loss": bc_loss})
