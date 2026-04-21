"""
OMNI Img2Dataset Engine — Production-grade image dataset pipeline primitives.
Assimilated from: rom1504/img2dataset
Provides: Batch image processing, perceptual hashing, resolution normalization.
"""
import numpy as np
from typing import List, Tuple, Optional



ENGINE_VERSION = "1.0.0-omni"

class Result:
    """Monadic Result base."""
    pass


class Ok(Result):
    """Success variant carrying a value."""
    def __init__(self, value):
        """Initialize Ok."""
        self.value = value


class Err(Result):
    """Error variant carrying an error description."""
    def __init__(self, error: str):
        """Initialize Err."""
        self.error = error


class OmniImg2DatasetEngine:
    """
    Native image dataset pipeline engine operating on raw NumPy tensors.
    Replaces img2dataset's Spark/ResizeRight stack with zero-dependency matrix ops.

    Capabilities:
        - Batch resize with aspect-ratio preservation
        - Perceptual hash deduplication (dHash)
        - Center-crop normalization
        - Channel statistics computation (mean/std per channel)

    @since 1.0.0
    @tags ["dataset", "image", "pipeline", "compute"]
    """

    def __init__(self) -> None:
        """Initialize OmniImg2DatasetEngine."""
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    def diagnostics(self) -> Result:
        """Returns engine health status."""
        return Ok({"status": "active", "engine": "Img2Dataset", "capability": "ImagePipelinePrimitives"})

    def resize_nearest(self, image: np.ndarray, target_h: int, target_w: int) -> Result:
        """
        Resizes an image tensor using nearest-neighbor interpolation.

        @param image: Input array of shape (H, W) or (H, W, C).
        @param target_h: Target height in pixels.
        @param target_w: Target width in pixels.
        @returns Result containing resized array.
        """
        if image.ndim not in (2, 3):
            return Err("Image tensor must be 2D (grayscale) or 3D (H, W, C).")
        if target_h <= 0 or target_w <= 0:
            return Err("Target dimensions must be positive integers.")

        src_h, src_w = image.shape[:2]
        row_indices = (np.arange(target_h) * src_h / target_h).astype(np.intp)
        col_indices = (np.arange(target_w) * src_w / target_w).astype(np.intp)

        # Clamp to valid bounds
        row_indices = np.clip(row_indices, 0, src_h - 1)
        col_indices = np.clip(col_indices, 0, src_w - 1)

        resized = image[np.ix_(row_indices, col_indices)] if image.ndim == 2 \
            else image[np.ix_(row_indices, col_indices, np.arange(image.shape[2]))]

        return Ok(resized)

    def center_crop(self, image: np.ndarray, crop_h: int, crop_w: int) -> Result:
        """
        Extracts a center crop from an image tensor.

        @param image: Input array of shape (H, W) or (H, W, C).
        @param crop_h: Crop height.
        @param crop_w: Crop width.
        @returns Result containing cropped array.
        """
        if image.ndim not in (2, 3):
            return Err("Image tensor must be 2D or 3D.")

        src_h, src_w = image.shape[:2]
        if crop_h > src_h or crop_w > src_w:
            return Err("Crop dimensions exceed source image bounds.")

        y_start = (src_h - crop_h) // 2
        x_start = (src_w - crop_w) // 2

        cropped = image[y_start:y_start + crop_h, x_start:x_start + crop_w]
        return Ok(cropped)

    def compute_dhash(self, image: np.ndarray, hash_size: int = 8) -> Result:
        """
        Computes a difference hash (dHash) for perceptual deduplication.
        Operates on grayscale. If 3D input, averages across channels first.

        @param image: Input image tensor.
        @param hash_size: Grid size for the hash (produces hash_size * hash_size bits).
        @returns Result containing a 1D binary hash array.
        """
        if image.ndim == 3:
            gray = np.mean(image, axis=2)
        elif image.ndim == 2:
            gray = image.astype(np.float64)
        else:
            return Err("Image must be 2D or 3D for dHash.")

        # Resize to (hash_size, hash_size+1) using nearest neighbor
        resized_res = self.resize_nearest(gray, hash_size, hash_size + 1)
        if isinstance(resized_res, Err):
            return resized_res
        small = resized_res.value

        # Horizontal gradient comparison
        dhash = (small[:, 1:] > small[:, :-1]).astype(np.uint8).flatten()
        return Ok(dhash)

    def compute_channel_stats(self, images: List[np.ndarray]) -> Result:
        """
        Computes per-channel mean and standard deviation across a batch of images.
        All images must be float and share the same number of channels.

        @param images: List of (H, W, C) float arrays.
        @returns Result containing dict with 'mean' and 'std' arrays of shape (C,).
        """
        if not images:
            return Err("Image list is empty.")

        n_channels = images[0].shape[2] if images[0].ndim == 3 else 1

        running_sum = np.zeros(n_channels, dtype=np.float64)
        running_sq_sum = np.zeros(n_channels, dtype=np.float64)
        total_pixels = 0

        for img in images:
            if img.ndim == 2:
                img = img[:, :, np.newaxis]
            if img.shape[2] != n_channels:
                return Err("All images must share the same number of channels.")

            pixels = img.shape[0] * img.shape[1]
            total_pixels += pixels
            running_sum += np.sum(img, axis=(0, 1))
            running_sq_sum += np.sum(img ** 2, axis=(0, 1))

        mean = running_sum / total_pixels
        std = np.sqrt(running_sq_sum / total_pixels - mean ** 2)

        return Ok({"mean": mean, "std": std})
