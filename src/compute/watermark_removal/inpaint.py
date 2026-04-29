import numpy as np

# OMNI Python Compute Layer: Watermark Removal Inpainting
# Fast marching / diffusion based deterministic inpainting for watermark erasure.
# Based on algorithmic foundations of image restoration.

class FastMarchingInpainter:
    def __init__(self, radius: int = 3):
        self.radius = radius

    def inpaint(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Inpaints a single channel image using diffusion equations.
        image: 2D array [H, W] containing pixel intensities.
        mask: 2D boolean array [H, W] where True indicates watermarks to be removed.
        """
        if image.shape != mask.shape:
            raise ValueError("Image and mask dimensions must match.")

        result = image.copy()
        h, w = result.shape

        # Iterative deterministic diffusion solver
        # Number of iterations controls the spread of the boundary
        iterations = 50 
        
        for _ in range(iterations):
            # We only update pixels inside the mask
            new_result = result.copy()
            for y in range(1, h - 1):
                for x in range(1, w - 1):
                    if mask[y, x]:
                        # Cross neighborhood averaging (Laplacian smoothing)
                        neighbors = [
                            result[y-1, x],
                            result[y+1, x],
                            result[y, x-1],
                            result[y, x+1]
                        ]
                        
                        # Only use valid source pixels (not inside mask if possible, or already diffused)
                        valid_neighbors = []
                        for i, (ny, nx) in enumerate([(y-1, x), (y+1, x), (y, x-1), (y, x+1)]):
                            # Weighted average based on mask status
                            weight = 0.5 if mask[ny, nx] else 1.0
                            valid_neighbors.append(neighbors[i] * weight)
                            
                        if sum(valid_neighbors) > 0:
                            new_result[y, x] = sum(valid_neighbors) / len(valid_neighbors)
            
            # Check convergence (L1 norm difference)
            diff = np.sum(np.abs(result - new_result))
            result = new_result
            
            if diff < 1e-4:
                break
                
        return result

def erase_watermark(img_data: np.ndarray, mask_data: np.ndarray) -> np.ndarray:
    inpainter = FastMarchingInpainter(radius=3)
    return inpainter.inpaint(img_data, mask_data)
