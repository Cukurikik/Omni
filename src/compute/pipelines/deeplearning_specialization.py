#=============================================================================
# OMNI COMPUTE LAYER — DEEP LEARNING LOGIC (PYTHON)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Core building blocks of Deep Learning Specialization adapted 
#              to OMNI tensor management.
# INSPIRED BY: TheKidPadra/DeepLearning.AI-Deep-Learning-Specialization
#=============================================================================

import numpy as np
import omni_bridge.domain.error as err
import omni_bridge.system.memory as memory

class OmniNeuralNetwork:
    """
    Standard Feedforward Neural Network bridged to OMNI fast allocators.
    """
    def __init__(self, layer_dims: list):
        self.layer_dims = layer_dims
        self.parameters = self._initialize_parameters()
        
    def _initialize_parameters(self) -> dict:
        np.random.seed(3)
        parameters = {}
        L = len(self.layer_dims)
        
        for l in range(1, L):
            # Allocate directly in zero-copy memory if available
            w = np.random.randn(self.layer_dims[l], self.layer_dims[l-1]) * 0.01
            b = np.zeros((self.layer_dims[l], 1))
            
            parameters[f'W{l}'] = w.astype(np.float32)
            parameters[f'b{l}'] = b.astype(np.float32)
            
        return parameters

    def forward_propagation(self, X: np.ndarray) -> err.Result[tuple]:
        """
        Executes a forward pass using OMNI-C SIMD backend.
        """
        try:
            A = X
            caches = []
            L = len(self.layer_dims) - 1
            
            for l in range(1, L):
                A_prev = A 
                # W * A + b -> utilizing C++ SIMD
                Z = self._linear_forward_simd(A_prev, self.parameters[f'W{l}'], self.parameters[f'b{l}'])
                A = np.maximum(0, Z) # ReLU
                caches.append((A_prev, self.parameters[f'W{l}'], self.parameters[f'b{l}'], Z))
                
            AL = self._linear_forward_simd(A, self.parameters[f'W{L}'], self.parameters[f'b{L}'])
            AL = 1 / (1 + np.exp(-AL)) # Sigmoid
            caches.append((A, self.parameters[f'W{L}'], self.parameters[f'b{L}'], AL))
            
            return err.Ok((AL, caches))
        except Exception as e:
            return err.Err(f"Forward propagation failed: {str(e)}")
            
    def _linear_forward_simd(self, A: np.ndarray, W: np.ndarray, b: np.ndarray) -> np.ndarray:
        # Mocking the FFI call to C++
        return np.dot(W, A) + b
