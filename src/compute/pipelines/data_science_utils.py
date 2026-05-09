#=============================================================================
# OMNI COMPUTE LAYER — DATA SCIENCE UTILITIES (PYTHON)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Production-grade data science utilities optimized for OMNI 
#              zero-copy dataframe bridging.
# INSPIRED BY: Suraj-G-Rao/Complete-Data-Science
#=============================================================================

import numpy as np
import omni_bridge.domain.error as err
import omni_bridge.system.memory as memory

class OmniDataScienceUtils:
    """
    Core utilities bridging Python Data Science workflows with OMNI C++/Rust accelerators.
    """
    
    @staticmethod
    def normalize_features_simd(data: np.ndarray) -> err.Result[np.ndarray]:
        """
        Z-score normalization using OMNI C++ AVX-512 backend.
        """
        try:
            if data.dtype != np.float32:
                data = data.astype(np.float32)
                
            out = np.empty_like(data)
            
            # Delegate to C++ backend, pointer extraction
            ptr_in = memory.get_pointer(data)
            ptr_out = memory.get_pointer(out)
            
            # This calls the C++ side directly, mutating 'out' in place
            memory.execute_simd_normalize(ptr_in, ptr_out, data.size)
            
            return err.Ok(out)
        except Exception as e:
            return err.Err(f"SIMD normalization failed: {str(e)}")

    @staticmethod
    def calculate_correlation_matrix(matrix: np.ndarray) -> err.Result[np.ndarray]:
        """
        Fast correlation matrix calculation via GPU/C++ backend.
        """
        try:
            if matrix.dtype != np.float32:
                matrix = matrix.astype(np.float32)
                
            cols = matrix.shape[1]
            out = np.empty((cols, cols), dtype=np.float32)
            
            memory.execute_simd_corr_matrix(memory.get_pointer(matrix), memory.get_pointer(out), matrix.shape[0], cols)
            return err.Ok(out)
        except Exception as e:
            return err.Err(f"Correlation matrix failed: {str(e)}")
