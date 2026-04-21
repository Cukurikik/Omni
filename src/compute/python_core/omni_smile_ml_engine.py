"""
OMNI Smile Ml Engine
====================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import numpy as np
from typing import Dict, Any, Tuple

class Result:
    """Monadic result pattern."""
    def __init__(self, value=None, error=None):
        """Initialize Result."""
        self.value = value
        self.error = error
        self.is_ok = error is None

    def unwrap(self):
        """Unwrap the value or raise on error."""
        if not self.is_ok:
            raise RuntimeError(self.error)
        return self.value

class OmniSmileMlEngine:
    """
    omni-smile-ml
    
    A zero-mock native engine simulating core Statistical Machine Intelligence.
    Focuses on a pure implementation of a Support Vector Machine (SVM) using 
    Sequential Minimal Optimization (SMO) traversing structural margin limits.
    """
    
    ENGINE_VERSION = "omni-s6-b8.1.0"
    
    def __init__(self, C: float = 1.0, tol: float = 1e-3, max_passes: int = 5, kernel_type: str = 'rbf', gamma: float = 0.5):
        """Initialize OmniSmileMlEngine."""
        self.C = C
        self.tol = tol
        self.max_passes = max_passes
        self.kernel_type = kernel_type
        self.gamma = gamma
        self.alphas = None
        self.b = 0.0
        self.X_train = None
        self.y_train = None

    def _kernel(self, x1: np.ndarray, x2: np.ndarray) -> float:
        if self.kernel_type == 'linear':
            return float(np.dot(x1, x2))
        elif self.kernel_type == 'rbf':
            diff = x1 - x2
            return float(np.exp(-self.gamma * np.dot(diff, diff)))
        return 0.0

    def fit(self, X: np.ndarray, y: np.ndarray) -> Result:
        """
        Solves SVM Dual Optimization problem using the Simplified SMO algorithm.
        y must be in {-1, 1}.
        """
        try:
            m, n = X.shape
            # Initialize alphas to zero
            self.alphas = np.zeros(m)
            self.b = 0.0
            self.X_train = X.copy()
            self.y_train = y.copy()
            
            passes = 0
            while passes < self.max_passes:
                num_changed_alphas = 0
                for i in range(m):
                    # Calculate f(x_i)
                    f_xi = self.b
                    for j in range(m):
                        f_xi += self.alphas[j] * self.y_train[j] * self._kernel(self.X_train[j], self.X_train[i])
                    
                    E_i = f_xi - self.y_train[i]
                    
                    if (self.y_train[i] * E_i < -self.tol and self.alphas[i] < self.C) or \
                       (self.y_train[i] * E_i > self.tol and self.alphas[i] > 0):
                           
                        # Select j randomly != i
                        j = i
                        while j == i:
                            j = np.random.randint(0, m)
                            
                        # Calculate f(x_j)
                        f_xj = self.b
                        for k in range(m):
                            f_xj += self.alphas[k] * self.y_train[k] * self._kernel(self.X_train[k], self.X_train[j])
                        E_j = f_xj - self.y_train[j]
                        
                        # Save old alphas
                        alpha_i_old = self.alphas[i].copy()
                        alpha_j_old = self.alphas[j].copy()
                        
                        # Compute L and H limits
                        if self.y_train[i] != self.y_train[j]:
                            L = max(0, self.alphas[j] - self.alphas[i])
                            H = min(self.C, self.C + self.alphas[j] - self.alphas[i])
                        else:
                            L = max(0, self.alphas[i] + self.alphas[j] - self.C)
                            H = min(self.C, self.alphas[i] + self.alphas[j])
                            
                        if L == H:
                            continue
                            
                        # Compute eta
                        eta = 2.0 * self._kernel(self.X_train[i], self.X_train[j]) \
                            - self._kernel(self.X_train[i], self.X_train[i]) \
                            - self._kernel(self.X_train[j], self.X_train[j])
                            
                        if eta >= 0:
                            continue
                            
                        # Update alpha_j
                        self.alphas[j] -= (self.y_train[j] * (E_i - E_j)) / eta
                        
                        # Clip alpha_j
                        if self.alphas[j] > H:
                            self.alphas[j] = H
                        elif self.alphas[j] < L:
                            self.alphas[j] = L
                            
                        if abs(self.alphas[j] - alpha_j_old) < 1e-5:
                            continue
                            
                        # Update alpha_i
                        self.alphas[i] += self.y_train[i] * self.y_train[j] * (alpha_j_old - self.alphas[j])
                        
                        # Compute b limits
                        b1 = self.b - E_i \
                             - self.y_train[i] * (self.alphas[i] - alpha_i_old) * self._kernel(self.X_train[i], self.X_train[i]) \
                             - self.y_train[j] * (self.alphas[j] - alpha_j_old) * self._kernel(self.X_train[i], self.X_train[j])
                             
                        b2 = self.b - E_j \
                             - self.y_train[i] * (self.alphas[i] - alpha_i_old) * self._kernel(self.X_train[i], self.X_train[j]) \
                             - self.y_train[j] * (self.alphas[j] - alpha_j_old) * self._kernel(self.X_train[j], self.X_train[j])
                             
                        if 0 < self.alphas[i] < self.C:
                            self.b = b1
                        elif 0 < self.alphas[j] < self.C:
                            self.b = b2
                        else:
                            self.b = (b1 + b2) / 2.0
                            
                        num_changed_alphas += 1
                        
                if num_changed_alphas == 0:
                    passes += 1
                else:
                    passes = 0
            
            support_vectors = np.sum(self.alphas > 0)
            return Result(value={"status": "fitted", "support_vectors": support_vectors})
            
        except Exception as e:
            return Result(error=f"SMO SVM fit error: {str(e)}")

    def predict(self, X: np.ndarray) -> Result:
        """Performs predict operation for OmniSmileMlEngine."""
        try:
            if self.alphas is None:
                return Result(error="Model not fitted.")
            
            m = X.shape[0]
            preds = np.zeros(m)
            
            for i in range(m):
                f_x = self.b
                for j in range(len(self.alphas)):
                    if self.alphas[j] > 0:
                        f_x += self.alphas[j] * self.y_train[j] * self._kernel(self.X_train[j], X[i])
                preds[i] = 1 if f_x >= 0 else -1
                
            return Result(value=preds)
        except Exception as e:
            return Result(error=f"SVM prediction error: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniSmileMlEngine."""
        return {
            "engine": "OmniSmileMlEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "components": ["SVM", "SMO-Algorithm", "RBF-Kernel"]
        }
