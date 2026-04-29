class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class ShapeInference:
    def __init__(self):
        pass

    def compute_broadcast_shape(self, shape_a: list[int], shape_b: list[int]) -> OmniResult:
        if shape_a is None or shape_b is None:
            return OmniResult(error="Shapes cannot be null")

        # Deterministic tensor broadcasting math (similar to NumPy/dfdx rules)
        # Dimensions are aligned right-to-left
        
        len_a = len(shape_a)
        len_b = len(shape_b)
        max_len = max(len_a, len_b)
        
        # Pad with 1s on the left
        padded_a = [1] * (max_len - len_a) + shape_a
        padded_b = [1] * (max_len - len_b) + shape_b
        
        out_shape = [0] * max_len
        
        for i in range(max_len):
            dim_a = padded_a[i]
            dim_b = padded_b[i]
            
            if dim_a == dim_b:
                out_shape[i] = dim_a
            elif dim_a == 1:
                out_shape[i] = dim_b
            elif dim_b == 1:
                out_shape[i] = dim_a
            else:
                return OmniResult(error=f"Shapes are not broadcastable: {shape_a} and {shape_b} (mismatch at dim {i-max_len})")

        return OmniResult(value=out_shape)
