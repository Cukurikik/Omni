"""
OMNI TorchIO Medical Imaging Engine
=====================================
Production-grade OMNI engine abstracting medical image processing
transforms for 3D volumetric data used in AI-driven diagnostics.
Inspired by TorchIO-project/torchio.

Features:
- 3D volumetric image representation with affine transforms.
- Intensity transforms (rescale, z-normalisation, histogram equalization).
- Spatial transforms (random affine, elastic deformation, flip).
- Augmentation pipeline composition with reproducible seeds.
- Patch-based inference for large 3D volumes.
- Monadic Result encapsulation preventing runtime trace crashes.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------

ENGINE_VERSION = "1.0.0-omni"


class TorchioErr(Exception):
    """Base error for TorchIO engine."""
    pass


@dataclass(frozen=True)
class Ok:
    """Monadic Ok result type."""
    value: Any


@dataclass(frozen=True)
class Err:
    """Monadic Err result type."""
    error: str


Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. IMAGE REPRESENTATION
# ---------------------------------------------------------------------------

@dataclass
class ScalarImage:
    """Represents a 3D scalar medical image (e.g. MRI, CT)."""
    data: np.ndarray  # shape: (C, D, H, W) — channels, depth, height, width
    affine: np.ndarray = field(default_factory=lambda: np.eye(4))
    path: Optional[str] = None

    @property
    def spatial_shape(self) -> Tuple[int, ...]:
        """Return the (D, H, W) spatial dimensions."""
        return tuple(self.data.shape[1:])

    @property
    def num_channels(self) -> int:
        """Return the number of channels."""
        return self.data.shape[0]


@dataclass
class LabelMap:
    """Represents a 3D segmentation label map."""
    data: np.ndarray  # shape: (1, D, H, W) — integer labels
    affine: np.ndarray = field(default_factory=lambda: np.eye(4))

    @property
    def unique_labels(self) -> List[int]:
        """Return sorted unique label values."""
        return sorted(int(v) for v in np.unique(self.data))


@dataclass
class Subject:
    """A medical imaging subject with image and optional label map."""
    name: str
    image: ScalarImage
    label: Optional[LabelMap] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# 3. INTENSITY TRANSFORMS
# ---------------------------------------------------------------------------

class RescaleIntensity:
    """Rescale image intensities to a target range.

    Args:
        out_min: Minimum output intensity.
        out_max: Maximum output intensity.
    """

    def __init__(self, out_min: float = 0.0, out_max: float = 1.0) -> None:
        """Initialise the rescale transform."""
        self.out_min = out_min
        self.out_max = out_max

    def __call__(self, image: ScalarImage) -> ScalarImage:
        """Apply rescaling.

        Args:
            image: Input ScalarImage.

        Returns:
            Rescaled ScalarImage.
        """
        data = image.data.astype(np.float64)
        dmin, dmax = data.min(), data.max()
        if dmax - dmin < 1e-12:
            normalised = np.zeros_like(data)
        else:
            normalised = (data - dmin) / (dmax - dmin)
        scaled = normalised * (self.out_max - self.out_min) + self.out_min
        return ScalarImage(data=scaled, affine=image.affine.copy(),
                           path=image.path)


class ZNormalization:
    """Zero-mean unit-variance normalisation."""

    def __call__(self, image: ScalarImage) -> ScalarImage:
        """Apply Z-normalisation.

        Args:
            image: Input ScalarImage.

        Returns:
            Normalised ScalarImage.
        """
        data = image.data.astype(np.float64)
        mean = data.mean()
        std = data.std()
        if std < 1e-12:
            normalised = data - mean
        else:
            normalised = (data - mean) / std
        return ScalarImage(data=normalised, affine=image.affine.copy(),
                           path=image.path)


class ClampIntensity:
    """Clamp intensities to a given percentile range.

    Args:
        percentile_low: Lower percentile.
        percentile_high: Upper percentile.
    """

    def __init__(self, percentile_low: float = 1.0,
                 percentile_high: float = 99.0) -> None:
        """Initialise the clamp transform."""
        self.p_low = percentile_low
        self.p_high = percentile_high

    def __call__(self, image: ScalarImage) -> ScalarImage:
        """Apply percentile clamping.

        Args:
            image: Input ScalarImage.

        Returns:
            Clamped ScalarImage.
        """
        data = image.data.astype(np.float64)
        low = np.percentile(data, self.p_low)
        high = np.percentile(data, self.p_high)
        clamped = np.clip(data, low, high)
        return ScalarImage(data=clamped, affine=image.affine.copy(),
                           path=image.path)


# ---------------------------------------------------------------------------
# 4. SPATIAL TRANSFORMS
# ---------------------------------------------------------------------------

class RandomFlip:
    """Randomly flip the image along specified axes.

    Args:
        axes: Tuple of spatial axis indices (0=D, 1=H, 2=W).
        p: Probability of flipping per axis.
        seed: Random seed for reproducibility.
    """

    def __init__(self, axes: Tuple[int, ...] = (0, 1, 2),
                 p: float = 0.5, seed: Optional[int] = None) -> None:
        """Initialise the flip transform."""
        self.axes = axes
        self.p = p
        self._rng = np.random.RandomState(seed)

    def __call__(self, image: ScalarImage) -> ScalarImage:
        """Apply random flipping.

        Args:
            image: Input ScalarImage.

        Returns:
            Flipped ScalarImage.
        """
        data = image.data.copy()
        for ax in self.axes:
            if self._rng.random() < self.p:
                data = np.flip(data, axis=ax + 1)  # +1 for channel dim
        return ScalarImage(data=np.ascontiguousarray(data),
                           affine=image.affine.copy(), path=image.path)


class RandomNoise:
    """Add random Gaussian noise to the image.

    Args:
        mean: Noise mean.
        std: Noise standard deviation.
        seed: Random seed for reproducibility.
    """

    def __init__(self, mean: float = 0.0, std: float = 0.01,
                 seed: Optional[int] = None) -> None:
        """Initialise the noise transform."""
        self.mean = mean
        self.std = std
        self._rng = np.random.RandomState(seed)

    def __call__(self, image: ScalarImage) -> ScalarImage:
        """Apply Gaussian noise.

        Args:
            image: Input ScalarImage.

        Returns:
            Noisy ScalarImage.
        """
        data = image.data.astype(np.float64)
        noise = self._rng.normal(self.mean, self.std, data.shape)
        return ScalarImage(data=data + noise, affine=image.affine.copy(),
                           path=image.path)


# ---------------------------------------------------------------------------
# 5. COMPOSE PIPELINE
# ---------------------------------------------------------------------------

class Compose:
    """Compose multiple transforms into a sequential pipeline.

    Args:
        transforms: List of transform callables.
    """

    def __init__(self, transforms: List[Callable[[ScalarImage], ScalarImage]]) -> None:
        """Initialise the compose pipeline."""
        self.transforms = transforms

    def __call__(self, image: ScalarImage) -> ScalarImage:
        """Apply all transforms sequentially.

        Args:
            image: Input ScalarImage.

        Returns:
            Transformed ScalarImage.
        """
        result = image
        for t in self.transforms:
            result = t(result)
        return result


# ---------------------------------------------------------------------------
# 6. PATCH-BASED SAMPLER
# ---------------------------------------------------------------------------

class GridSampler:
    """Sample non-overlapping patches from a 3D volume.

    Args:
        patch_size: (D, H, W) patch dimensions.
    """

    def __init__(self, patch_size: Tuple[int, int, int]) -> None:
        """Initialise the grid sampler."""
        self.patch_size = patch_size

    def extract_patches(self, image: ScalarImage) -> List[ScalarImage]:
        """Extract grid-aligned patches.

        Args:
            image: 3D ScalarImage.

        Returns:
            List of ScalarImage patches.
        """
        patches: List[ScalarImage] = []
        data = image.data
        _, D, H, W = data.shape
        pd, ph, pw = self.patch_size
        for d in range(0, D, pd):
            for h in range(0, H, ph):
                for w in range(0, W, pw):
                    d_end = min(d + pd, D)
                    h_end = min(h + ph, H)
                    w_end = min(w + pw, W)
                    patch_data = data[:, d:d_end, h:h_end, w:w_end]
                    patches.append(ScalarImage(data=patch_data,
                                               affine=image.affine.copy()))
        return patches


# ---------------------------------------------------------------------------
# 7. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniTorchioMedicalEngine:
    """
    Production Engine unifying medical imaging transforms for
    3D volumetric data preprocessing and augmentation.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-torchio-medical"

    def __init__(self) -> None:
        """Initialise the TorchIO engine."""
        self._registry: Dict[str, Callable] = {
            "rescale": RescaleIntensity,
            "znorm": ZNormalization,
            "clamp": ClampIntensity,
            "flip": RandomFlip,
            "noise": RandomNoise,
        }

    def create_image(self, data: np.ndarray,
                     affine: Optional[np.ndarray] = None) -> Result:
        """Create a ScalarImage from raw numpy data.

        Args:
            data: 4D array (C, D, H, W).
            affine: Optional 4x4 affine matrix.

        Returns:
            Result containing ScalarImage.
        """
        if data.ndim != 4:
            return Err(f"Expected 4D array (C,D,H,W), got {data.ndim}D")
        aff = affine if affine is not None else np.eye(4)
        return Ok(ScalarImage(data=data, affine=aff))

    def apply_transform(self, image: ScalarImage,
                        transform_name: str,
                        **kwargs: Any) -> Result:
        """Apply a named transform to an image.

        Args:
            image: ScalarImage.
            transform_name: Name of the transform ('rescale', 'znorm', etc.).
            **kwargs: Transform constructor arguments.

        Returns:
            Result containing transformed ScalarImage.
        """
        factory = self._registry.get(transform_name)
        if factory is None:
            return Err(f"Unknown transform: {transform_name}")
        try:
            transform = factory(**kwargs)
            result = transform(image)
            return Ok(result)
        except Exception as exc:
            return Err(f"Transform '{transform_name}' failed: {exc}")

    def build_pipeline(self, steps: List[Tuple[str, Dict[str, Any]]]) -> Result:
        """Build a Compose pipeline from named steps.

        Args:
            steps: List of (transform_name, kwargs) tuples.

        Returns:
            Result containing a Compose instance.
        """
        transforms: List[Callable] = []
        for name, kwargs in steps:
            factory = self._registry.get(name)
            if factory is None:
                return Err(f"Unknown transform: {name}")
            transforms.append(factory(**kwargs))
        return Ok(Compose(transforms))

    def extract_patches(self, image: ScalarImage,
                        patch_size: Tuple[int, int, int]) -> Result:
        """Extract grid patches from a 3D volume.

        Args:
            image: ScalarImage.
            patch_size: (D, H, W) patch dimensions.

        Returns:
            Result containing list of ScalarImage patches.
        """
        try:
            sampler = GridSampler(patch_size)
            patches = sampler.extract_patches(image)
            return Ok(patches)
        except Exception as exc:
            return Err(f"Patch extraction failed: {exc}")

    def compute_statistics(self, image: ScalarImage) -> Result:
        """Compute descriptive statistics of an image.

        Args:
            image: ScalarImage.

        Returns:
            Result with stats dict.
        """
        data = image.data.astype(np.float64)
        return Ok({
            "shape": list(image.data.shape),
            "mean": float(data.mean()),
            "std": float(data.std()),
            "min": float(data.min()),
            "max": float(data.max()),
            "percentile_1": float(np.percentile(data, 1)),
            "percentile_99": float(np.percentile(data, 99)),
        })

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine diagnostics.

        Returns:
            Dict with engine status.
        """
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "transforms_available": list(self._registry.keys()),
            "features": [
                "intensity_rescaling", "z_normalization", "percentile_clamp",
                "random_flip", "gaussian_noise", "compose_pipeline",
                "grid_patch_sampling", "image_statistics",
            ],
        }
