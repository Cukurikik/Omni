"""
OMNI Surface Defect Detection Engine — Industrial visual inspection primitives.

Assimilated from: Charmve/Surface-Defect-Detection (3k ★)
Implements core algorithms for surface defect detection:
  - Texture analysis: LBP (Local Binary Pattern), GLCM
  - Anomaly scoring: Mahalanobis distance, reconstruction error
  - Segmentation: adaptive thresholding, connected components
  - Morphological operations: erosion, dilation, opening, closing
  - Edge detection: Sobel, Canny (NMS + hysteresis)
  - Template matching: Normalized Cross-Correlation (NCC)
  - Statistical process control: control chart limits, Cpk

OMNI Domain: compute/ (Python)
CODE RULE 001-005 compliant. Only numpy dependency.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np


ENGINE_VERSION: str = "1.0.0-omni"
ENGINE_NAME: str = "OmniSurfaceDefectEngine"


# ---------------------------------------------------------------------------
# Monadic Result
# ---------------------------------------------------------------------------

class Result:
    """Monadic Result type for error handling."""
    pass


class Ok(Result):
    """Monadic Ok result type."""
    def __init__(self, value: Any) -> None:
        """Initialize Ok."""
        self.value = value


class Err(Result):
    """Monadic Err result type."""
    def __init__(self, error: str) -> None:
        """Initialize Err."""
        self.error = error


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class OmniSurfaceDefectEngine:
    """Production-grade surface defect detection engine.

    Provides image analysis primitives for industrial visual inspection:
      - Texture descriptors (LBP, GLCM)
      - Anomaly scoring for defect detection
      - Image segmentation & morphology
      - Edge detection (Sobel, Canny)
      - Template matching
      - Statistical quality control

    @since 1.0.0
    @tags ["defect-detection", "industrial", "quality-control", "computer-vision", "compute"]
    """

    VERSION = ENGINE_VERSION
    ENGINE_ID = ENGINE_NAME

    def __init__(self) -> None:
        """Initialize OmniSurfaceDefectEngine."""
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    def diagnostics(self) -> Result:
        """Return engine health diagnostics."""
        return Ok({
            "engine": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "capabilities": [
                "lbp", "glcm", "mahalanobis", "adaptive_threshold",
                "connected_components", "morphology",
                "sobel", "canny", "template_matching", "cpk",
            ],
        })

    # -----------------------------------------------------------------
    # 1. TEXTURE ANALYSIS
    # -----------------------------------------------------------------

    def compute_lbp(self, image: np.ndarray, radius: int = 1) -> Result:
        """Compute Local Binary Pattern (LBP) descriptor.

        For each pixel, compare with 8 neighbors at given radius.
        LBP code = sum of 2^i for each neighbor >= center.

        @param image: 2D grayscale image (H, W).
        @param radius: Radius for neighbor comparison (default 1).
        @returns Result containing LBP image (H-2r, W-2r).
        """
        if image.ndim != 2:
            return Err("image must be 2D grayscale.")
        if radius < 1:
            return Err("radius must be >= 1.")

        h, w = image.shape
        if h < 2 * radius + 1 or w < 2 * radius + 1:
            return Err("Image too small for given radius.")

        # 8 neighbor offsets for circular LBP
        offsets = [
            (-radius, 0), (-radius, radius), (0, radius), (radius, radius),
            (radius, 0), (radius, -radius), (0, -radius), (-radius, -radius),
        ]

        out_h = h - 2 * radius
        out_w = w - 2 * radius
        lbp = np.zeros((out_h, out_w), dtype=np.uint8)

        for i in range(out_h):
            for j in range(out_w):
                center = image[i + radius, j + radius]
                code = 0
                for bit, (dy, dx) in enumerate(offsets):
                    ny, nx = i + radius + dy, j + radius + dx
                    if image[ny, nx] >= center:
                        code |= (1 << bit)
                lbp[i, j] = code

        return Ok(lbp)

    def compute_lbp_histogram(self, lbp: np.ndarray, n_bins: int = 256) -> Result:
        """Compute normalized histogram of LBP codes.

        @param lbp: LBP image from compute_lbp.
        @param n_bins: Number of bins (default 256 for standard 8-bit LBP).
        @returns Result containing normalized histogram array.
        """
        if lbp.ndim != 2:
            return Err("lbp must be 2D.")
        hist, _ = np.histogram(lbp.ravel(), bins=n_bins, range=(0, n_bins))
        hist = hist.astype(np.float64)
        total = hist.sum()
        if total > 0:
            hist /= total
        return Ok(hist)

    def compute_glcm(
        self, image: np.ndarray, distance: int = 1, angle: float = 0.0, levels: int = 256
    ) -> Result:
        """Compute Gray-Level Co-occurrence Matrix (GLCM).

        @param image: 2D grayscale image (integer values).
        @param distance: Pixel distance (default 1).
        @param angle: Angle in radians (0=horizontal, pi/2=vertical).
        @param levels: Number of gray levels (default 256).
        @returns Result containing (levels, levels) GLCM matrix.
        """
        if image.ndim != 2:
            return Err("image must be 2D.")

        dy = int(round(distance * math.sin(angle)))
        dx = int(round(distance * math.cos(angle)))

        h, w = image.shape
        img = np.clip(image, 0, levels - 1).astype(int)
        glcm = np.zeros((levels, levels), dtype=np.float64)

        for i in range(h):
            for j in range(w):
                ni, nj = i + dy, j + dx
                if 0 <= ni < h and 0 <= nj < w:
                    glcm[img[i, j], img[ni, nj]] += 1

        total = glcm.sum()
        if total > 0:
            glcm /= total
        return Ok(glcm)

    def glcm_features(self, glcm: np.ndarray) -> Result:
        """Extract Haralick features from GLCM.

        @param glcm: Normalized GLCM matrix.
        @returns Result containing dict with contrast, dissimilarity,
                 homogeneity, energy, correlation, entropy.
        """
        if glcm.ndim != 2 or glcm.shape[0] != glcm.shape[1]:
            return Err("GLCM must be square 2D.")

        n = glcm.shape[0]
        i_idx, j_idx = np.meshgrid(np.arange(n), np.arange(n), indexing='ij')

        contrast = float(np.sum(glcm * (i_idx - j_idx) ** 2))
        dissimilarity = float(np.sum(glcm * np.abs(i_idx - j_idx)))
        homogeneity = float(np.sum(glcm / (1 + (i_idx - j_idx) ** 2)))
        energy = float(np.sum(glcm ** 2))

        eps = 1e-10
        entropy = float(-np.sum(glcm * np.log(glcm + eps)))

        mu_i = np.sum(i_idx * glcm)
        mu_j = np.sum(j_idx * glcm)
        sigma_i = np.sqrt(np.sum(glcm * (i_idx - mu_i) ** 2))
        sigma_j = np.sqrt(np.sum(glcm * (j_idx - mu_j) ** 2))
        if sigma_i > eps and sigma_j > eps:
            correlation = float(np.sum(glcm * (i_idx - mu_i) * (j_idx - mu_j)) / (sigma_i * sigma_j))
        else:
            correlation = 0.0

        return Ok({
            "contrast": contrast,
            "dissimilarity": dissimilarity,
            "homogeneity": homogeneity,
            "energy": energy,
            "entropy": entropy,
            "correlation": correlation,
        })

    # -----------------------------------------------------------------
    # 2. ANOMALY SCORING
    # -----------------------------------------------------------------

    def mahalanobis_distance(
        self, x: np.ndarray, mean: np.ndarray, cov_inv: np.ndarray
    ) -> Result:
        """Compute Mahalanobis distance.

        d = sqrt((x - mu)^T @ Σ^{-1} @ (x - mu))

        @param x: (N, D) sample matrix or (D,) single sample.
        @param mean: (D,) mean vector.
        @param cov_inv: (D, D) inverse covariance matrix.
        @returns Result containing (N,) distance array or scalar.
        """
        if x.ndim == 1:
            diff = x - mean
            dist = float(np.sqrt(diff @ cov_inv @ diff))
            return Ok(dist)
        elif x.ndim == 2:
            diff = x - mean
            left = diff @ cov_inv
            dist = np.sqrt(np.sum(left * diff, axis=1))
            return Ok(dist)
        return Err("x must be 1D or 2D.")

    def reconstruction_error(self, original: np.ndarray, reconstructed: np.ndarray) -> Result:
        """Compute pixel-wise reconstruction error (MSE map).

        @param original: 2D image.
        @param reconstructed: 2D reconstructed image.
        @returns Result containing dict with 'error_map' and 'mean_error'.
        """
        if original.shape != reconstructed.shape:
            return Err("Shape mismatch.")
        error_map = (original.astype(np.float64) - reconstructed.astype(np.float64)) ** 2
        return Ok({"error_map": error_map, "mean_error": float(np.mean(error_map))})

    # -----------------------------------------------------------------
    # 3. SEGMENTATION
    # -----------------------------------------------------------------

    def adaptive_threshold(
        self, image: np.ndarray, block_size: int = 11, c: float = 2.0
    ) -> Result:
        """Adaptive mean thresholding for defect segmentation.

        Threshold = local_mean - c

        @param image: 2D grayscale image.
        @param block_size: Size of local neighborhood (must be odd).
        @param c: Constant subtracted from local mean.
        @returns Result containing binary mask (0/1).
        """
        if image.ndim != 2:
            return Err("image must be 2D.")
        if block_size % 2 == 0:
            return Err("block_size must be odd.")

        h, w = image.shape
        pad = block_size // 2
        padded = np.pad(image.astype(np.float64), pad, mode='reflect')

        local_mean = np.zeros_like(image, dtype=np.float64)
        for i in range(h):
            for j in range(w):
                block = padded[i:i + block_size, j:j + block_size]
                local_mean[i, j] = np.mean(block)

        binary = (image.astype(np.float64) > (local_mean - c)).astype(np.uint8)
        return Ok(binary)

    def connected_components(self, binary: np.ndarray) -> Result:
        """Label connected components in binary image (4-connectivity).

        @param binary: 2D binary image (0/1).
        @returns Result containing dict with 'labels' (int map), 'n_components'.
        """
        if binary.ndim != 2:
            return Err("binary must be 2D.")

        h, w = binary.shape
        labels = np.zeros((h, w), dtype=np.int32)
        current_label = 0

        def flood_fill(r: int, c: int, label: int) -> None:
            stack = [(r, c)]
            while stack:
                y, x = stack.pop()
                if y < 0 or y >= h or x < 0 or x >= w:
                    continue
                if labels[y, x] != 0 or binary[y, x] == 0:
                    continue
                labels[y, x] = label
                stack.extend([(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)])

        for i in range(h):
            for j in range(w):
                if binary[i, j] == 1 and labels[i, j] == 0:
                    current_label += 1
                    flood_fill(i, j, current_label)

        return Ok({"labels": labels, "n_components": current_label})

    # -----------------------------------------------------------------
    # 4. MORPHOLOGICAL OPERATIONS
    # -----------------------------------------------------------------

    def erode(self, binary: np.ndarray, kernel_size: int = 3) -> Result:
        """Binary erosion (minimum filter).

        @param binary: 2D binary image (0/1).
        @param kernel_size: Size of square structuring element (must be odd).
        @returns Result containing eroded binary image.
        """
        if binary.ndim != 2:
            return Err("binary must be 2D.")
        if kernel_size % 2 == 0:
            return Err("kernel_size must be odd.")

        pad = kernel_size // 2
        padded = np.pad(binary, pad, mode='constant', constant_values=0)
        h, w = binary.shape
        result = np.zeros_like(binary)
        for i in range(h):
            for j in range(w):
                block = padded[i:i + kernel_size, j:j + kernel_size]
                result[i, j] = np.min(block)
        return Ok(result)

    def dilate(self, binary: np.ndarray, kernel_size: int = 3) -> Result:
        """Binary dilation (maximum filter).

        @param binary: 2D binary image (0/1).
        @param kernel_size: Size of square structuring element (must be odd).
        @returns Result containing dilated binary image.
        """
        if binary.ndim != 2:
            return Err("binary must be 2D.")
        if kernel_size % 2 == 0:
            return Err("kernel_size must be odd.")

        pad = kernel_size // 2
        padded = np.pad(binary, pad, mode='constant', constant_values=0)
        h, w = binary.shape
        result = np.zeros_like(binary)
        for i in range(h):
            for j in range(w):
                block = padded[i:i + kernel_size, j:j + kernel_size]
                result[i, j] = np.max(block)
        return Ok(result)

    def morphological_open(self, binary: np.ndarray, kernel_size: int = 3) -> Result:
        """Morphological opening = erosion then dilation (removes small objects).

        @param binary: 2D binary image.
        @param kernel_size: Structuring element size.
        @returns Result containing opened image.
        """
        res = self.erode(binary, kernel_size)
        if isinstance(res, Err):
            return res
        return self.dilate(res.value, kernel_size)

    def morphological_close(self, binary: np.ndarray, kernel_size: int = 3) -> Result:
        """Morphological closing = dilation then erosion (fills small holes).

        @param binary: 2D binary image.
        @param kernel_size: Structuring element size.
        @returns Result containing closed image.
        """
        res = self.dilate(binary, kernel_size)
        if isinstance(res, Err):
            return res
        return self.erode(res.value, kernel_size)

    # -----------------------------------------------------------------
    # 5. EDGE DETECTION
    # -----------------------------------------------------------------

    def sobel_edges(self, image: np.ndarray) -> Result:
        """Compute Sobel edge magnitude and direction.

        @param image: 2D grayscale image.
        @returns Result containing dict with 'magnitude' and 'direction'.
        """
        if image.ndim != 2:
            return Err("image must be 2D.")

        kx = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]], dtype=np.float64)
        ky = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]], dtype=np.float64)

        h, w = image.shape
        img = image.astype(np.float64)
        padded = np.pad(img, 1, mode='reflect')

        gx = np.zeros((h, w), dtype=np.float64)
        gy = np.zeros((h, w), dtype=np.float64)
        for i in range(h):
            for j in range(w):
                patch = padded[i:i + 3, j:j + 3]
                gx[i, j] = np.sum(patch * kx)
                gy[i, j] = np.sum(patch * ky)

        magnitude = np.sqrt(gx ** 2 + gy ** 2)
        direction = np.arctan2(gy, gx)
        return Ok({"magnitude": magnitude, "direction": direction})

    def canny_edge(
        self, image: np.ndarray, low_thresh: float = 20, high_thresh: float = 50
    ) -> Result:
        """Simplified Canny edge detection (Sobel + NMS + hysteresis).

        @param image: 2D grayscale image.
        @param low_thresh: Low hysteresis threshold.
        @param high_thresh: High hysteresis threshold.
        @returns Result containing binary edge map.
        """
        sobel_res = self.sobel_edges(image)
        if isinstance(sobel_res, Err):
            return sobel_res

        mag = sobel_res.value["magnitude"]
        d = sobel_res.value["direction"]
        h, w = mag.shape

        # Non-maximum suppression
        nms = np.zeros_like(mag)
        angle = (np.degrees(d) % 180).astype(int)

        for i in range(1, h - 1):
            for j in range(1, w - 1):
                a = angle[i, j]
                if (0 <= a < 22) or (157 <= a <= 180):
                    n1, n2 = mag[i, j - 1], mag[i, j + 1]
                elif 22 <= a < 67:
                    n1, n2 = mag[i - 1, j + 1], mag[i + 1, j - 1]
                elif 67 <= a < 112:
                    n1, n2 = mag[i - 1, j], mag[i + 1, j]
                else:
                    n1, n2 = mag[i - 1, j - 1], mag[i + 1, j + 1]

                if mag[i, j] >= n1 and mag[i, j] >= n2:
                    nms[i, j] = mag[i, j]

        # Hysteresis thresholding
        strong = (nms >= high_thresh).astype(np.uint8)
        weak = ((nms >= low_thresh) & (nms < high_thresh)).astype(np.uint8)

        edges = strong.copy()
        # Connect weak edges adjacent to strong edges
        for i in range(1, h - 1):
            for j in range(1, w - 1):
                if weak[i, j] == 1:
                    if np.max(strong[i - 1:i + 2, j - 1:j + 2]) > 0:
                        edges[i, j] = 1

        return Ok(edges)

    # -----------------------------------------------------------------
    # 6. TEMPLATE MATCHING
    # -----------------------------------------------------------------

    def normalized_cross_correlation(
        self, image: np.ndarray, template: np.ndarray
    ) -> Result:
        """Compute Normalized Cross-Correlation (NCC) score map.

        NCC = sum((I - mu_I) * (T - mu_T)) / (N * sigma_I * sigma_T)

        @param image: 2D grayscale image.
        @param template: 2D template patch (smaller than image).
        @returns Result containing dict with 'score_map', 'best_loc', 'best_score'.
        """
        if image.ndim != 2 or template.ndim != 2:
            return Err("Both must be 2D.")
        th, tw = template.shape
        ih, iw = image.shape
        if th > ih or tw > iw:
            return Err("Template larger than image.")

        img = image.astype(np.float64)
        tpl = template.astype(np.float64)
        t_mean = np.mean(tpl)
        t_std = np.std(tpl)
        if t_std < 1e-10:
            t_std = 1e-10

        oh = ih - th + 1
        ow = iw - tw + 1
        score_map = np.zeros((oh, ow), dtype=np.float64)

        for i in range(oh):
            for j in range(ow):
                patch = img[i:i + th, j:j + tw]
                p_mean = np.mean(patch)
                p_std = np.std(patch)
                if p_std < 1e-10:
                    p_std = 1e-10
                ncc = np.mean((patch - p_mean) * (tpl - t_mean)) / (p_std * t_std)
                score_map[i, j] = ncc

        best_idx = np.unravel_index(np.argmax(score_map), score_map.shape)
        return Ok({
            "score_map": score_map,
            "best_loc": (int(best_idx[0]), int(best_idx[1])),
            "best_score": float(score_map[best_idx]),
        })

    # -----------------------------------------------------------------
    # 7. STATISTICAL PROCESS CONTROL
    # -----------------------------------------------------------------

    def control_chart_limits(
        self, measurements: np.ndarray, n_sigma: float = 3.0
    ) -> Result:
        """Compute control chart limits (UCL, CL, LCL).

        UCL = mean + n_sigma * std
        LCL = mean - n_sigma * std

        @param measurements: 1D array of quality measurements.
        @param n_sigma: Number of standard deviations (default 3).
        @returns Result containing dict with 'ucl', 'cl', 'lcl', 'out_of_control'.
        """
        if measurements.ndim != 1 or len(measurements) == 0:
            return Err("measurements must be non-empty 1D.")

        cl = float(np.mean(measurements))
        sigma = float(np.std(measurements))
        ucl = cl + n_sigma * sigma
        lcl = cl - n_sigma * sigma
        ooc = bool(np.any((measurements > ucl) | (measurements < lcl)))

        return Ok({"ucl": ucl, "cl": cl, "lcl": lcl, "out_of_control": ooc})

    def compute_cpk(
        self, measurements: np.ndarray, usl: float, lsl: float
    ) -> Result:
        """Compute process capability index Cpk.

        Cpk = min((USL - mu) / (3*sigma), (mu - LSL) / (3*sigma))

        @param measurements: 1D measurement array.
        @param usl: Upper specification limit.
        @param lsl: Lower specification limit.
        @returns Result containing dict with 'cpk', 'cp', 'capable' (Cpk >= 1.33).
        """
        if measurements.ndim != 1 or len(measurements) < 2:
            return Err("Need at least 2 measurements.")
        if usl <= lsl:
            return Err("USL must be > LSL.")

        mu = float(np.mean(measurements))
        sigma = float(np.std(measurements, ddof=1))
        if sigma < 1e-15:
            return Ok({"cpk": float('inf'), "cp": float('inf'), "capable": True})

        cp = (usl - lsl) / (6 * sigma)
        cpu = (usl - mu) / (3 * sigma)
        cpl = (mu - lsl) / (3 * sigma)
        cpk = min(cpu, cpl)

        return Ok({"cpk": cpk, "cp": cp, "capable": cpk >= 1.33})
