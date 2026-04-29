class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class MobileViTMath:
    def __init__(self):
        pass

    def compute_self_attention(self, q: list[float], k: list[float], v: list[float], d_k: float) -> OmniResult:
        if not q or not k or not v or len(q) != len(k) or len(k) != len(v):
            return OmniResult(error="Invalid QKV vectors")

        if d_k <= 0:
            return OmniResult(error="d_k must be positive")

        # Deterministic mathematical formulation of scaled dot-product attention
        # Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V
        
        n = len(q)
        scores = [0.0] * n
        
        # 1. Dot product (Q * K^T) / sqrt(d_k)
        # Using 1D simulation for deterministic proof
        scale = d_k ** 0.5
        for i in range(n):
            scores[i] = (q[i] * k[i]) / scale

        # 2. Softmax mathematically
        max_score = max(scores)
        exp_sum = 0.0
        exp_scores = [0.0] * n
        
        import math
        for i in range(n):
            exp_scores[i] = math.exp(scores[i] - max_score) # numeric stability
            exp_sum += exp_scores[i]
            
        for i in range(n):
            exp_scores[i] /= exp_sum
            
        # 3. Multiply by V
        output = [0.0] * n
        for i in range(n):
            output[i] = exp_scores[i] * v[i]

        return OmniResult(value={
            "attention_output": output,
            "attention_weights": exp_scores
        })
