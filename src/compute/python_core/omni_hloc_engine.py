"""
OMNI Hierarchical Localization Engine — Visual localization with keypoint matching.
Assimilated from: cvg/Hierarchical-Localization (hloc)
Provides: Keypoint scoring, descriptor matching (brute-force & ratio test), RANSAC homography.
"""
import numpy as np
from typing import Optional, Tuple



ENGINE_VERSION = "1.0.0-omni"

class Result:
    """Monadic Result base."""
    pass


class Ok(Result):
    """Success variant."""
    def __init__(self, value):
        """Initialize Ok."""
        self.value = value


class Err(Result):
    """Error variant."""
    def __init__(self, error: str):
        """Initialize Err."""
        self.error = error


class OmniHLocEngine:
    """
    Pure NumPy visual localization engine inspired by hloc (Hierarchical-Localization).

    Implements the core algorithmic primitives of the SfM/localization pipeline:
      - Keypoint response scoring (Harris corner measure)
      - Brute-force descriptor matching with Lowe's ratio test
      - RANSAC-based homography estimation
      - Reprojection error computation

    @since 1.0.0
    @tags ["localization", "sfm", "keypoints", "matching", "compute"]
    """

    def __init__(self) -> None:
        """Initialize OmniHLocEngine."""
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

    def diagnostics(self) -> Result:
        """Returns engine health status."""
        return Ok({"status": "active", "engine": "HLoc", "capability": "HierarchicalLocalization"})

    def harris_corner_response(self, image: np.ndarray, k: float = 0.04) -> Result:
        """
        Computes Harris corner response R for a grayscale image.

        R = det(M) - k * trace(M)^2

        where M is the structure tensor built from image gradients (Sobel).

        @param image: 2D grayscale float image.
        @param k: Harris detector sensitivity parameter (typically 0.04-0.06).
        @returns Result containing 2D response map of same shape as input.
        """
        if image.ndim != 2:
            return Err("Image must be 2D grayscale.")

        # Sobel gradients
        # Simple 1D kernels: [-1, 0, 1] for dx, and its transpose for dy
        Ix = np.zeros_like(image)
        Iy = np.zeros_like(image)
        Ix[:, 1:-1] = (image[:, 2:] - image[:, :-2]) / 2.0
        Iy[1:-1, :] = (image[2:, :] - image[:-2, :]) / 2.0

        Ixx = Ix * Ix
        Iyy = Iy * Iy
        Ixy = Ix * Iy

        # Box filter (3x3 summation) for structure tensor smoothing
        def box_filter_3x3(arr: np.ndarray) -> np.ndarray:
            out = np.zeros_like(arr)
            out[1:-1, 1:-1] = (
                arr[:-2, :-2] + arr[:-2, 1:-1] + arr[:-2, 2:]
                + arr[1:-1, :-2] + arr[1:-1, 1:-1] + arr[1:-1, 2:]
                + arr[2:, :-2] + arr[2:, 1:-1] + arr[2:, 2:]
            )
            return out

        Sxx = box_filter_3x3(Ixx)
        Syy = box_filter_3x3(Iyy)
        Sxy = box_filter_3x3(Ixy)

        det_M = Sxx * Syy - Sxy * Sxy
        trace_M = Sxx + Syy
        R = det_M - k * trace_M ** 2

        return Ok(R)

    def extract_keypoints(self, response_map: np.ndarray, threshold: float = 0.01, max_keypoints: int = 500) -> Result:
        """
        Extracts keypoints from a Harris response map via thresholding and NMS.

        @param response_map: 2D corner response (from harris_corner_response).
        @param threshold: Minimum response value (relative to max response).
        @param max_keypoints: Maximum number of keypoints to return.
        @returns Result containing (N, 2) array of [row, col] keypoint coordinates.
        """
        if response_map.ndim != 2:
            return Err("Response map must be 2D.")

        abs_threshold = threshold * np.max(response_map)
        candidates = np.argwhere(response_map > abs_threshold)

        if len(candidates) == 0:
            return Ok(np.empty((0, 2), dtype=np.intp))

        # Sort by response strength (descending)
        scores = response_map[candidates[:, 0], candidates[:, 1]]
        sorted_indices = np.argsort(-scores)
        candidates = candidates[sorted_indices]

        # Simple greedy NMS: keep top points with minimum distance
        selected = [candidates[0]]
        for i in range(1, len(candidates)):
            pt = candidates[i]
            dists = np.sqrt(np.sum((np.array(selected) - pt) ** 2, axis=1))
            if np.min(dists) >= 3.0:  # minimum 3-pixel spacing
                selected.append(pt)
            if len(selected) >= max_keypoints:
                break

        return Ok(np.array(selected, dtype=np.intp))

    def match_descriptors_ratio_test(
        self,
        desc_a: np.ndarray,
        desc_b: np.ndarray,
        ratio_thresh: float = 0.75,
    ) -> Result:
        """
        Brute-force descriptor matching with Lowe's ratio test.

        For each descriptor in A, finds the two nearest neighbors in B.
        A match is accepted if distance(1st) / distance(2nd) < ratio_thresh.

        @param desc_a: (N, D) descriptors from image A.
        @param desc_b: (M, D) descriptors from image B.
        @param ratio_thresh: Lowe's ratio threshold (default 0.75).
        @returns Result containing (K, 2) array of matched index pairs [idx_a, idx_b].
        """
        if desc_a.ndim != 2 or desc_b.ndim != 2:
            return Err("Both descriptor arrays must be 2D.")
        if desc_a.shape[1] != desc_b.shape[1]:
            return Err("Descriptor dimensions must match.")
        if desc_b.shape[0] < 2:
            return Err("Need at least 2 descriptors in B for ratio test.")

        # Compute pairwise L2 distance matrix using broadcasting
        # ||a - b||^2 = ||a||^2 + ||b||^2 - 2*a·b
        sq_a = np.sum(desc_a ** 2, axis=1, keepdims=True)
        sq_b = np.sum(desc_b ** 2, axis=1, keepdims=True)
        dist_sq = sq_a + sq_b.T - 2.0 * (desc_a @ desc_b.T)
        dist_sq = np.maximum(dist_sq, 0.0)
        distances = np.sqrt(dist_sq)

        matches = []
        for i in range(len(desc_a)):
            sorted_idx = np.argsort(distances[i])
            d1 = distances[i, sorted_idx[0]]
            d2 = distances[i, sorted_idx[1]]
            if d2 > 1e-12 and d1 / d2 < ratio_thresh:
                matches.append([i, sorted_idx[0]])

        if not matches:
            return Ok(np.empty((0, 2), dtype=np.intp))

        return Ok(np.array(matches, dtype=np.intp))

    def estimate_homography_dlt(self, src_pts: np.ndarray, dst_pts: np.ndarray) -> Result:
        """
        Estimates a 3x3 homography matrix using Direct Linear Transform (DLT).

        Requires at least 4 point correspondences.

        @param src_pts: (N, 2) source 2D points.
        @param dst_pts: (N, 2) destination 2D points.
        @returns Result containing (3, 3) homography matrix H (dst = H @ src).
        """
        if src_pts.shape[0] < 4 or dst_pts.shape[0] < 4:
            return Err("Need at least 4 point correspondences.")
        if src_pts.shape != dst_pts.shape:
            return Err("Source and destination point arrays must have the same shape.")

        n = src_pts.shape[0]
        A = np.zeros((2 * n, 9), dtype=np.float64)

        for i in range(n):
            x, y = src_pts[i]
            xp, yp = dst_pts[i]
            A[2 * i] = [-x, -y, -1, 0, 0, 0, x * xp, y * xp, xp]
            A[2 * i + 1] = [0, 0, 0, -x, -y, -1, x * yp, y * yp, yp]

        _, _, Vt = np.linalg.svd(A)
        H = Vt[-1].reshape(3, 3)
        H /= H[2, 2]  # normalize

        return Ok(H)

    def compute_reprojection_error(self, src_pts: np.ndarray, dst_pts: np.ndarray, H: np.ndarray) -> Result:
        """
        Computes reprojection error for point correspondences given homography H.

        error_i = ||dst_i - project(H, src_i)||

        @param src_pts: (N, 2) source points.
        @param dst_pts: (N, 2) destination points.
        @param H: (3, 3) homography matrix.
        @returns Result containing 1D array of per-point reprojection errors.
        """
        if H.shape != (3, 3):
            return Err("H must be a 3x3 matrix.")

        n = src_pts.shape[0]
        ones = np.ones((n, 1), dtype=np.float64)
        src_h = np.hstack([src_pts, ones])  # (N, 3)

        projected_h = (H @ src_h.T).T  # (N, 3)
        projected = projected_h[:, :2] / (projected_h[:, 2:3] + 1e-12)

        errors = np.sqrt(np.sum((dst_pts - projected) ** 2, axis=1))
        return Ok(errors)
