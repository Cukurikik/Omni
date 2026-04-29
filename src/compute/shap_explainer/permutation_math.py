import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class ShapleyMath:
    def __init__(self):
        pass

    def compute_permutation_weight(self, coalition_size: int, num_features: int) -> OmniResult:
        if coalition_size < 0 or num_features <= 0:
            return OmniResult(error="Invalid coalition size or total features")
            
        if coalition_size >= num_features:
            return OmniResult(error="Coalition size must be strictly less than total features")

        # Deterministic Shapley Kernel Weight calculation
        # Weight(S) = (M - 1) / ( (M choose |S|) * |S| * (M - |S|) )
        
        try:
            m_choose_s = math.comb(num_features, coalition_size)
            
            denominator = m_choose_s * coalition_size * (num_features - coalition_size)
            
            if denominator == 0:
                 # In exact SHAP, weight is inf for S=0 or S=M, but we restrict domain
                 return OmniResult(error="Denominator is zero, invalid domain for kernel weight")
                 
            weight = (num_features - 1) / denominator
            
            return OmniResult(value=weight)
        except Exception as e:
            return OmniResult(error=str(e))
