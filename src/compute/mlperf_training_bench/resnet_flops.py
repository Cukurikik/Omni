class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class MLPerfMath:
    def __init__(self):
        pass

    def compute_resnet_flops(self, batch_size: int, image_size: int, num_layers: int) -> OmniResult:
        if batch_size <= 0 or image_size <= 0 or num_layers <= 0:
            return OmniResult(error="Batch size, image size, and number of layers must be positive integers.")

        # Deterministic simulation of FLOPs calculation for ResNet-style architectures
        # For a standard ResNet-50, a 224x224 image takes ~3.8 to 4 GFLOPs per forward pass.
        try:
            # Baseline FLOPs per pixel per layer (approximate scaling factor)
            base_flops_per_pixel = 25.0
            
            pixels = image_size * image_size
            flops_per_image = pixels * num_layers * base_flops_per_pixel
            
            # Account for backward pass (typically 2x forward pass FLOPs)
            total_flops_per_image = flops_per_image * 3.0
            
            total_batch_flops = total_flops_per_image * batch_size
            
            return OmniResult(value={
                "batch_flops": total_batch_flops,
                "tflops": total_batch_flops / 1e12
            })
        except Exception as e:
            return OmniResult(error=str(e))
