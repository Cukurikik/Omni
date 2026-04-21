"""
OMNI DeepLabCut Engine
========================
Production-grade markerless pose estimation engine inspired by
DeepLabCut/DeepLabCut. Implements the full pose estimation pipeline:
body part detection, multi-animal tracking, skeleton construction,
and behavioral analysis.

Extracted Patterns:
  - Pose estimation via heatmap + offset regression
  - Part Affinity Fields (PAFs) for multi-animal association
  - Non-Maximum Suppression for keypoint detection
  - Skeleton graph construction and rendering
  - Multi-animal assembly: bipartite matching
  - Kalman filter-based tracking
  - Behavioral feature extraction (velocity, acceleration, angles)
  - Project configuration management
  - Data augmentation for training

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union
from enum import Enum

import numpy as np

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------


ENGINE_VERSION = "1.0.0-omni"

class DLCError(Exception):
    """Base error for DeepLabCut engine."""

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
# 2. DATA STRUCTURES
# ---------------------------------------------------------------------------

@dataclass
class Keypoint:
    """A single detected keypoint (body part)."""
    name: str
    x: float
    y: float
    confidence: float = 1.0

    @property
    def position(self) -> Tuple[float, float]:
        """Execute position operation for Keypoint."""
        return (self.x, self.y)


@dataclass
class Skeleton:
    """
    A skeleton definition: named keypoints and their connections.
    """
    keypoints: List[str]
    connections: List[Tuple[str, str]]
    name: str = "default"

    @property
    def num_joints(self) -> int:
        """Execute num joints operation for Skeleton."""
        return len(self.keypoints)

    @property
    def num_limbs(self) -> int:
        """Execute num limbs operation for Skeleton."""
        return len(self.connections)


@dataclass
class Pose:
    """
    A detected pose instance: a set of keypoints for one animal/person.
    """
    keypoints: Dict[str, Keypoint]
    instance_id: int = -1
    score: float = 0.0

    @property
    def num_detected(self) -> int:
        """Execute num detected operation for Pose."""
        return sum(1 for kp in self.keypoints.values() if kp.confidence > 0.1)

    def get_keypoint(self, name: str) -> Optional[Keypoint]:
        """Retrieve keypoint from Pose."""
        return self.keypoints.get(name)

    def to_array(self, keypoint_names: List[str]) -> np.ndarray:
        """Convert to (num_joints, 3) array: [x, y, confidence]."""
        arr = np.zeros((len(keypoint_names), 3), dtype=np.float32)
        for i, name in enumerate(keypoint_names):
            kp = self.keypoints.get(name)
            if kp:
                arr[i] = [kp.x, kp.y, kp.confidence]
        return arr


@dataclass
class Track:
    """A tracked animal/person across multiple frames."""
    track_id: int
    poses: List[Tuple[int, Pose]]   # (frame_idx, Pose)
    active: bool = True

    @property
    def num_frames(self) -> int:
        """Execute num frames operation for Track."""
        return len(self.poses)

    def last_pose(self) -> Optional[Pose]:
        """Execute last pose operation for Track."""
        if self.poses:
            return self.poses[-1][1]
        return None

    def trajectory(self, keypoint_name: str) -> np.ndarray:
        """Get trajectory for a specific keypoint: (N, 2) [x, y]."""
        points = []
        for _, pose in self.poses:
            kp = pose.get_keypoint(keypoint_name)
            if kp and kp.confidence > 0.1:
                points.append([kp.x, kp.y])
        return np.array(points, dtype=np.float32) if points else np.empty((0, 2), dtype=np.float32)


@dataclass
class ProjectConfig:
    """DeepLabCut project configuration."""
    project_name: str
    scorer: str = "omni-dlc"
    skeleton: Optional[Skeleton] = None
    num_animals: int = 1
    image_size: Tuple[int, int] = (256, 256)
    heatmap_sigma: float = 5.0
    paf_sigma: float = 3.0
    confidence_threshold: float = 0.3
    nms_radius: int = 5


# ---------------------------------------------------------------------------
# 3. HEATMAP GENERATION & DETECTION
# ---------------------------------------------------------------------------

def generate_heatmap(
    keypoints: List[Keypoint],
    height: int,
    width: int,
    sigma: float = 5.0,
) -> np.ndarray:
    """
    Generate Gaussian heatmaps for keypoints.

    Args:
        keypoints: list of Keypoint objects
        height, width: heatmap spatial dimensions
        sigma: Gaussian standard deviation

    Returns:
        heatmaps: (num_keypoints, height, width)
    """
    num_kp = len(keypoints)
    heatmaps = np.zeros((num_kp, height, width), dtype=np.float32)

    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)

    for i, kp in enumerate(keypoints):
        if kp.confidence < 0.01:
            continue
        d2 = (xx - kp.x) ** 2 + (yy - kp.y) ** 2
        heatmaps[i] = np.exp(-d2 / (2 * sigma ** 2))

    return heatmaps


def detect_keypoints_from_heatmaps(
    heatmaps: np.ndarray,
    keypoint_names: List[str],
    threshold: float = 0.3,
    nms_radius: int = 5,
) -> List[Keypoint]:
    """
    Detect keypoints from predicted heatmaps using NMS.

    Args:
        heatmaps: (num_keypoints, H, W)
        keypoint_names: list of names
        threshold: confidence threshold
        nms_radius: NMS suppression radius

    Returns:
        list of detected Keypoints
    """
    detected = []
    num_kp, h, w = heatmaps.shape

    for i in range(num_kp):
        hm = heatmaps[i]

        # Local maximum detection (NMS)
        max_hm = np.zeros_like(hm)
        for y in range(h):
            for x in range(w):
                y_lo = max(0, y - nms_radius)
                y_hi = min(h, y + nms_radius + 1)
                x_lo = max(0, x - nms_radius)
                x_hi = min(w, x + nms_radius + 1)
                if hm[y, x] == np.max(hm[y_lo:y_hi, x_lo:x_hi]):
                    max_hm[y, x] = hm[y, x]

        # Find peaks above threshold
        peaks = np.argwhere(max_hm >= threshold)
        if len(peaks) > 0:
            # Take the strongest peak
            best_idx = np.argmax([max_hm[p[0], p[1]] for p in peaks])
            y, x = peaks[best_idx]
            conf = float(max_hm[y, x])
            name = keypoint_names[i] if i < len(keypoint_names) else f"kp_{i}"
            detected.append(Keypoint(name=name, x=float(x), y=float(y), confidence=conf))
        else:
            name = keypoint_names[i] if i < len(keypoint_names) else f"kp_{i}"
            detected.append(Keypoint(name=name, x=0.0, y=0.0, confidence=0.0))

    return detected


# ---------------------------------------------------------------------------
# 4. PART AFFINITY FIELDS (Multi-Animal)
# ---------------------------------------------------------------------------

def generate_paf(
    connections: List[Tuple[Keypoint, Keypoint]],
    height: int,
    width: int,
    sigma: float = 3.0,
) -> np.ndarray:
    """
    Generate Part Affinity Fields for limb connections.

    Args:
        connections: pairs of connected keypoints
        height, width: spatial dims
        sigma: width of the PAF

    Returns:
        pafs: (num_connections * 2, height, width) — x and y components
    """
    num_conn = len(connections)
    pafs = np.zeros((num_conn * 2, height, width), dtype=np.float32)

    for ci, (kp_a, kp_b) in enumerate(connections):
        if kp_a.confidence < 0.01 or kp_b.confidence < 0.01:
            continue

        dx = kp_b.x - kp_a.x
        dy = kp_b.y - kp_a.y
        length = math.sqrt(dx ** 2 + dy ** 2) + 1e-8

        # Unit vector along limb
        ux = dx / length
        uy = dy / length

        # Normal vector
        nx = -uy
        ny = ux

        for y in range(height):
            for x in range(width):
                # Project point onto limb axis
                vx = x - kp_a.x
                vy = y - kp_a.y
                proj = vx * ux + vy * uy  # along limb
                perp = abs(vx * nx + vy * ny)  # perpendicular distance

                if 0 <= proj <= length and perp <= sigma:
                    pafs[ci * 2, y, x] = ux
                    pafs[ci * 2 + 1, y, x] = uy

    return pafs


def score_paf_connection(
    paf_x: np.ndarray,
    paf_y: np.ndarray,
    kp_a: Keypoint,
    kp_b: Keypoint,
    num_samples: int = 10,
) -> float:
    """
    Score a candidate connection by integrating PAF along the limb.

    Returns:
        score: average dot product along the limb
    """
    dx = kp_b.x - kp_a.x
    dy = kp_b.y - kp_a.y
    length = math.sqrt(dx ** 2 + dy ** 2) + 1e-8
    ux = dx / length
    uy = dy / length

    h, w = paf_x.shape
    score = 0.0

    for t in range(num_samples):
        frac = t / max(num_samples - 1, 1)
        sx = kp_a.x + frac * dx
        sy = kp_a.y + frac * dy

        xi = int(np.clip(sx, 0, w - 1))
        yi = int(np.clip(sy, 0, h - 1))

        score += paf_x[yi, xi] * ux + paf_y[yi, xi] * uy

    return score / num_samples


# ---------------------------------------------------------------------------
# 5. MULTI-ANIMAL ASSEMBLY (BIPARTITE MATCHING)
# ---------------------------------------------------------------------------

def hungarian_assignment(cost_matrix: np.ndarray) -> List[Tuple[int, int]]:
    """
    Simple greedy bipartite matching (approximation of Hungarian algorithm).

    Args:
        cost_matrix: (M, N) cost matrix (lower is better match)

    Returns:
        List of (row, col) matched pairs
    """
    m, n = cost_matrix.shape
    assignments = []
    used_rows = set()
    used_cols = set()

    # Greedy: always pick the smallest remaining cost
    flat_order = np.argsort(cost_matrix.flatten())

    for flat_idx in flat_order:
        r = int(flat_idx // n)
        c = int(flat_idx % n)
        if r not in used_rows and c not in used_cols:
            assignments.append((r, c))
            used_rows.add(r)
            used_cols.add(c)
        if len(assignments) >= min(m, n):
            break

    return assignments


def assemble_multi_animal_poses(
    all_candidates: Dict[str, List[Keypoint]],
    skeleton: Skeleton,
    paf_scores: Optional[Dict[Tuple[str, str], np.ndarray]] = None,
    max_animals: int = 5,
) -> List[Pose]:
    """
    Assemble per-keypoint detections into multi-animal pose instances.

    Uses greedy bipartite matching on spatial proximity.
    """
    # Start with first keypoint type as seeds
    if not skeleton.keypoints:
        return []

    first_kp_name = skeleton.keypoints[0]
    seeds = all_candidates.get(first_kp_name, [])

    poses: List[Dict[str, Keypoint]] = []
    for seed in seeds[:max_animals]:
        poses.append({first_kp_name: seed})

    # Assign remaining keypoints
    for kp_name in skeleton.keypoints[1:]:
        candidates = all_candidates.get(kp_name, [])
        if not candidates or not poses:
            continue

        # Build cost matrix: distance between existing pose centroids and candidates
        cost = np.full((len(poses), len(candidates)), 1e6, dtype=np.float32)
        for pi, pose_dict in enumerate(poses):
            # Centroid of existing keypoints
            xs = [kp.x for kp in pose_dict.values() if kp.confidence > 0.1]
            ys = [kp.y for kp in pose_dict.values() if kp.confidence > 0.1]
            if not xs:
                continue
            cx, cy = np.mean(xs), np.mean(ys)
            for ci, cand in enumerate(candidates):
                cost[pi, ci] = math.sqrt((cand.x - cx) ** 2 + (cand.y - cy) ** 2)

        matches = hungarian_assignment(cost)
        for pi, ci in matches:
            if cost[pi, ci] < 500:  # distance threshold
                poses[pi][kp_name] = candidates[ci]

    result = []
    for i, pose_dict in enumerate(poses):
        score = np.mean([kp.confidence for kp in pose_dict.values()])
        result.append(Pose(keypoints=pose_dict, instance_id=i, score=float(score)))

    return result


# ---------------------------------------------------------------------------
# 6. KALMAN FILTER TRACKER
# ---------------------------------------------------------------------------

class KalmanTracker:
    """
    Simple Kalman filter for 2D keypoint tracking.

    State: [x, y, vx, vy]
    """

    def __init__(self, initial_position: Tuple[float, float],
                 process_noise: float = 1.0,
                 measurement_noise: float = 5.0):
        """Initialize KalmanTracker."""
        self.state = np.array([initial_position[0], initial_position[1], 0.0, 0.0],
                              dtype=np.float64)
        self.P = np.eye(4, dtype=np.float64) * 100.0  # Covariance

        dt = 1.0
        self.F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ], dtype=np.float64)

        self.H = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
        ], dtype=np.float64)

        self.Q = np.eye(4, dtype=np.float64) * process_noise
        self.R = np.eye(2, dtype=np.float64) * measurement_noise

    def predict(self) -> np.ndarray:
        """Predict next state."""
        self.state = self.F @ self.state
        self.P = self.F @ self.P @ self.F.T + self.Q
        return self.state[:2].copy()

    def update(self, measurement: Tuple[float, float]) -> np.ndarray:
        """Update with measurement."""
        z = np.array([measurement[0], measurement[1]], dtype=np.float64)
        y = z - self.H @ self.state
        S = self.H @ self.P @ self.H.T + self.R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.state = self.state + K @ y
        self.P = (np.eye(4) - K @ self.H) @ self.P
        return self.state[:2].copy()

    @property
    def position(self) -> Tuple[float, float]:
        """Execute position operation for KalmanTracker."""
        return (float(self.state[0]), float(self.state[1]))

    @property
    def velocity(self) -> Tuple[float, float]:
        """Execute velocity operation for KalmanTracker."""
        return (float(self.state[2]), float(self.state[3]))


class MultiAnimalTracker:
    """
    Track multiple animals across frames using Kalman filters.

    Assigns new detections to existing tracks via proximity matching.
    """

    def __init__(self, max_lost_frames: int = 10, distance_threshold: float = 80.0):
        """Initialize MultiAnimalTracker."""
        self.tracks: List[Track] = []
        self.kalman_filters: Dict[int, Dict[str, KalmanTracker]] = {}
        self.next_id = 0
        self.max_lost_frames = max_lost_frames
        self.distance_threshold = distance_threshold
        self._lost_count: Dict[int, int] = {}

    def update(self, poses: List[Pose], frame_idx: int) -> List[Track]:
        """
        Update tracker with new pose detections.

        Args:
            poses: detected poses in current frame
            frame_idx: current frame number

        Returns:
            active tracks
        """
        if not self.tracks:
            # Initialize tracks
            for pose in poses:
                self._create_track(pose, frame_idx)
            return [t for t in self.tracks if t.active]

        # Predict positions
        for tid, kf_dict in self.kalman_filters.items():
            for kp_name, kf in kf_dict.items():
                kf.predict()

        # Build cost matrix between existing tracks and new detections
        active_tracks = [t for t in self.tracks if t.active]
        if not active_tracks or not poses:
            for pose in poses:
                self._create_track(pose, frame_idx)
            return [t for t in self.tracks if t.active]

        cost = np.full((len(active_tracks), len(poses)), 1e6, dtype=np.float32)
        for ti, track in enumerate(active_tracks):
            last = track.last_pose()
            if last is None:
                continue
            for pi, pose in enumerate(poses):
                dist = self._pose_distance(last, pose)
                cost[ti, pi] = dist

        matches = hungarian_assignment(cost)
        matched_tracks = set()
        matched_poses = set()

        for ti, pi in matches:
            if cost[ti, pi] < self.distance_threshold:
                track = active_tracks[ti]
                pose = poses[pi]
                pose.instance_id = track.track_id
                track.poses.append((frame_idx, pose))
                self._lost_count[track.track_id] = 0

                # Update Kalman filters
                for kp_name, kp in pose.keypoints.items():
                    if kp.confidence > 0.1:
                        if track.track_id in self.kalman_filters and kp_name in self.kalman_filters[track.track_id]:
                            self.kalman_filters[track.track_id][kp_name].update((kp.x, kp.y))

                matched_tracks.add(ti)
                matched_poses.add(pi)

        # Handle lost tracks
        for ti, track in enumerate(active_tracks):
            if ti not in matched_tracks:
                self._lost_count[track.track_id] = self._lost_count.get(track.track_id, 0) + 1
                if self._lost_count[track.track_id] > self.max_lost_frames:
                    track.active = False

        # Create new tracks for unmatched poses
        for pi, pose in enumerate(poses):
            if pi not in matched_poses:
                self._create_track(pose, frame_idx)

        return [t for t in self.tracks if t.active]

    def _create_track(self, pose: Pose, frame_idx: int):
        """Create a new track from a pose."""
        tid = self.next_id
        self.next_id += 1
        pose.instance_id = tid
        track = Track(track_id=tid, poses=[(frame_idx, pose)])
        self.tracks.append(track)
        self._lost_count[tid] = 0

        # Initialize Kalman filters for each keypoint
        self.kalman_filters[tid] = {}
        for kp_name, kp in pose.keypoints.items():
            if kp.confidence > 0.1:
                self.kalman_filters[tid][kp_name] = KalmanTracker((kp.x, kp.y))

    def _pose_distance(self, pose_a: Pose, pose_b: Pose) -> float:
        """Compute distance between two poses."""
        dists = []
        for name in pose_a.keypoints:
            if name in pose_b.keypoints:
                kp_a = pose_a.keypoints[name]
                kp_b = pose_b.keypoints[name]
                if kp_a.confidence > 0.1 and kp_b.confidence > 0.1:
                    d = math.sqrt((kp_a.x - kp_b.x) ** 2 + (kp_a.y - kp_b.y) ** 2)
                    dists.append(d)
        return float(np.mean(dists)) if dists else 1e6


# ---------------------------------------------------------------------------
# 7. BEHAVIORAL ANALYSIS
# ---------------------------------------------------------------------------

def compute_velocity(trajectory: np.ndarray, fps: float = 30.0) -> np.ndarray:
    """
    Compute velocity from trajectory.

    Args:
        trajectory: (N, 2) [x, y] positions
        fps: frames per second

    Returns:
        velocity: (N-1,) speed values
    """
    if len(trajectory) < 2:
        return np.array([], dtype=np.float32)
    diff = np.diff(trajectory, axis=0)
    speed = np.sqrt(np.sum(diff ** 2, axis=1)) * fps
    return speed


def compute_acceleration(trajectory: np.ndarray, fps: float = 30.0) -> np.ndarray:
    """Compute acceleration from trajectory."""
    vel = compute_velocity(trajectory, fps)
    if len(vel) < 2:
        return np.array([], dtype=np.float32)
    return np.diff(vel) * fps


def compute_joint_angle(
    kp_a: Keypoint,
    kp_vertex: Keypoint,
    kp_b: Keypoint,
) -> float:
    """
    Compute angle at vertex between segments a-vertex and vertex-b.

    Returns angle in degrees [0, 180].
    """
    va = np.array([kp_a.x - kp_vertex.x, kp_a.y - kp_vertex.y])
    vb = np.array([kp_b.x - kp_vertex.x, kp_b.y - kp_vertex.y])

    cos_angle = np.dot(va, vb) / (np.linalg.norm(va) * np.linalg.norm(vb) + 1e-8)
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    return float(np.degrees(np.arccos(cos_angle)))


def compute_distance_between_keypoints(kp_a: Keypoint, kp_b: Keypoint) -> float:
    """Euclidean distance between two keypoints."""
    return float(math.sqrt((kp_a.x - kp_b.x) ** 2 + (kp_a.y - kp_b.y) ** 2))


def classify_behavior(
    velocity: float,
    acceleration: float,
    thresholds: Optional[Dict[str, float]] = None,
) -> str:
    """
    Simple behavioral classification based on motion features.

    Categories: resting, walking, running, turning
    """
    if thresholds is None:
        thresholds = {"rest": 2.0, "walk": 15.0, "run": 50.0}

    if velocity < thresholds["rest"]:
        return "resting"
    elif velocity < thresholds["walk"]:
        return "walking"
    elif velocity < thresholds["run"]:
        if abs(acceleration) > 20.0:
            return "turning"
        return "running"
    else:
        return "fast_running"


# ---------------------------------------------------------------------------
# 8. DATA AUGMENTATION
# ---------------------------------------------------------------------------

def augment_keypoints(
    keypoints: List[Keypoint],
    image_size: Tuple[int, int],
    flip_horizontal: bool = False,
    scale: float = 1.0,
    rotation_deg: float = 0.0,
    translate: Tuple[float, float] = (0.0, 0.0),
) -> List[Keypoint]:
    """
    Augment keypoint coordinates.

    Applied in order: scale → rotate → translate → flip.
    """
    h, w = image_size
    cx, cy = w / 2.0, h / 2.0
    rad = math.radians(rotation_deg)

    augmented = []
    for kp in keypoints:
        x, y = kp.x, kp.y

        # Scale around center
        x = cx + (x - cx) * scale
        y = cy + (y - cy) * scale

        # Rotate around center
        dx, dy = x - cx, y - cy
        x = cx + dx * math.cos(rad) - dy * math.sin(rad)
        y = cy + dx * math.sin(rad) + dy * math.cos(rad)

        # Translate
        x += translate[0]
        y += translate[1]

        # Flip
        if flip_horizontal:
            x = w - x

        augmented.append(Keypoint(name=kp.name, x=x, y=y, confidence=kp.confidence))

    return augmented


# ---------------------------------------------------------------------------
# 9. PRESET SKELETONS
# ---------------------------------------------------------------------------

def mouse_skeleton() -> Skeleton:
    """Standard mouse skeleton (DeepLabCut mouse dataset)."""
    return Skeleton(
        name="mouse",
        keypoints=["snout", "left_ear", "right_ear", "neck",
                    "left_forepaw", "right_forepaw", "spine_mid",
                    "left_hindpaw", "right_hindpaw", "tail_base",
                    "tail_mid", "tail_tip"],
        connections=[
            ("snout", "neck"), ("left_ear", "neck"), ("right_ear", "neck"),
            ("neck", "left_forepaw"), ("neck", "right_forepaw"),
            ("neck", "spine_mid"), ("spine_mid", "left_hindpaw"),
            ("spine_mid", "right_hindpaw"), ("spine_mid", "tail_base"),
            ("tail_base", "tail_mid"), ("tail_mid", "tail_tip"),
        ],
    )


def human_skeleton() -> Skeleton:
    """COCO-style human skeleton."""
    return Skeleton(
        name="human_coco",
        keypoints=["nose", "left_eye", "right_eye", "left_ear", "right_ear",
                    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
                    "left_wrist", "right_wrist", "left_hip", "right_hip",
                    "left_knee", "right_knee", "left_ankle", "right_ankle"],
        connections=[
            ("nose", "left_eye"), ("nose", "right_eye"),
            ("left_eye", "left_ear"), ("right_eye", "right_ear"),
            ("left_shoulder", "right_shoulder"),
            ("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist"),
            ("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"),
            ("left_shoulder", "left_hip"), ("right_shoulder", "right_hip"),
            ("left_hip", "right_hip"),
            ("left_hip", "left_knee"), ("left_knee", "left_ankle"),
            ("right_hip", "right_knee"), ("right_knee", "right_ankle"),
        ],
    )


# ---------------------------------------------------------------------------
# 10. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniDeepLabCutEngine:
    """
    Production-grade markerless pose estimation engine for OMNI.

    Provides:
      - Heatmap generation and keypoint detection
      - Part Affinity Fields for multi-animal pose assembly
      - Kalman filter-based multi-animal tracking
      - Skeleton graph for any body plan
      - Behavioral analysis (velocity, acceleration, angles)
      - Data augmentation for training
      - COCO human and mouse preset skeletons
    """

    VERSION = "1.0.0"
    ENGINE_ID = "omni-deeplabcut"

    def __init__(self, config: Optional[ProjectConfig] = None):
        """Initialize OmniDeepLabCutEngine."""
        self.config = config or ProjectConfig(
            project_name="omni-dlc",
            skeleton=mouse_skeleton(),
        )
        self.tracker = MultiAnimalTracker()

    # --- Skeleton ---

    def create_skeleton(self, name: str, keypoints: List[str],
                        connections: List[Tuple[str, str]]) -> Skeleton:
        """Create a custom skeleton."""
        return Skeleton(name=name, keypoints=keypoints, connections=connections)

    def preset_mouse(self) -> Skeleton:
        """Performs preset mouse operation for OmniDeepLabCutEngine."""
        return mouse_skeleton()

    def preset_human(self) -> Skeleton:
        """Performs preset human operation for OmniDeepLabCutEngine."""
        return human_skeleton()

    # --- Heatmap ---

    def generate_heatmaps(self, keypoints: List[Keypoint],
                          height: int = 64, width: int = 64) -> np.ndarray:
        """Generate training heatmaps from GT keypoints."""
        return generate_heatmap(keypoints, height, width, self.config.heatmap_sigma)

    def detect_keypoints(self, heatmaps: np.ndarray,
                         keypoint_names: Optional[List[str]] = None) -> List[Keypoint]:
        """Detect keypoints from predicted heatmaps."""
        names = keypoint_names or (self.config.skeleton.keypoints if self.config.skeleton else [])
        return detect_keypoints_from_heatmaps(
            heatmaps, names,
            threshold=self.config.confidence_threshold,
            nms_radius=self.config.nms_radius,
        )

    # --- PAF ---

    def generate_pafs(self, connections: List[Tuple[Keypoint, Keypoint]],
                      height: int = 64, width: int = 64) -> np.ndarray:
        """Generate PAF ground truth."""
        return generate_paf(connections, height, width, self.config.paf_sigma)

    def score_connection(self, paf: np.ndarray, kp_a: Keypoint,
                         kp_b: Keypoint, limb_idx: int) -> float:
        """Score a candidate limb connection using PAF."""
        paf_x = paf[limb_idx * 2]
        paf_y = paf[limb_idx * 2 + 1]
        return score_paf_connection(paf_x, paf_y, kp_a, kp_b)

    # --- Multi-animal assembly ---

    def assemble_poses(self, all_candidates: Dict[str, List[Keypoint]],
                       skeleton: Optional[Skeleton] = None) -> List[Pose]:
        """Assemble multi-animal poses from per-keypoint detections."""
        skel = skeleton or self.config.skeleton
        if skel is None:
            return []
        return assemble_multi_animal_poses(all_candidates, skel,
                                           max_animals=self.config.num_animals)

    # --- Tracking ---

    def track_poses(self, poses: List[Pose], frame_idx: int) -> List[Track]:
        """Update tracker with new detections."""
        return self.tracker.update(poses, frame_idx)

    def get_tracks(self) -> List[Track]:
        """Get all tracks (active + inactive)."""
        return self.tracker.tracks

    # --- Behavioral Analysis ---

    def compute_velocity(self, trajectory: np.ndarray,
                         fps: float = 30.0) -> np.ndarray:
        """Performs compute velocity operation for OmniDeepLabCutEngine."""
        return compute_velocity(trajectory, fps)

    def compute_acceleration(self, trajectory: np.ndarray,
                             fps: float = 30.0) -> np.ndarray:
        """Performs compute acceleration operation for OmniDeepLabCutEngine."""
        return compute_acceleration(trajectory, fps)

    def compute_angle(self, kp_a: Keypoint, kp_vertex: Keypoint,
                      kp_b: Keypoint) -> float:
        """Performs compute angle operation for OmniDeepLabCutEngine."""
        return compute_joint_angle(kp_a, kp_vertex, kp_b)

    def compute_distance(self, kp_a: Keypoint, kp_b: Keypoint) -> float:
        """Performs compute distance operation for OmniDeepLabCutEngine."""
        return compute_distance_between_keypoints(kp_a, kp_b)

    def classify_behavior(self, velocity: float, acceleration: float) -> str:
        """Performs classify behavior operation for OmniDeepLabCutEngine."""
        return classify_behavior(velocity, acceleration)

    # --- Augmentation ---

    def augment_keypoints(self, keypoints: List[Keypoint],
                          flip: bool = False, scale: float = 1.0,
                          rotation: float = 0.0) -> List[Keypoint]:
        """Performs augment keypoints operation for OmniDeepLabCutEngine."""
        return augment_keypoints(keypoints, self.config.image_size,
                                 flip_horizontal=flip, scale=scale,
                                 rotation_deg=rotation)

    # --- Full pipeline ---

    def predict_single_frame(self, heatmaps: np.ndarray,
                             frame_idx: int = 0) -> Dict[str, Any]:
        """
        Full single-frame pipeline: detect → assemble → track.

        Args:
            heatmaps: (num_keypoints, H, W) predicted heatmaps
            frame_idx: frame number

        Returns:
            dict with poses, tracks, and metadata
        """
        if self.config.skeleton is None:
            return {"error": "No skeleton configured"}

        keypoints = self.detect_keypoints(heatmaps)

        # Group by name for assembly
        candidates: Dict[str, List[Keypoint]] = {}
        for kp in keypoints:
            if kp.name not in candidates:
                candidates[kp.name] = []
            candidates[kp.name].append(kp)

        poses = self.assemble_poses(candidates)
        active_tracks = self.track_poses(poses, frame_idx)

        return {
            "keypoints": keypoints,
            "poses": poses,
            "active_tracks": len(active_tracks),
            "total_tracks": len(self.tracker.tracks),
            "frame": frame_idx,
        }

    # --- Health ---

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniDeepLabCutEngine."""
        skel_info = {}
        if self.config.skeleton:
            skel_info = {
                "skeleton_name": self.config.skeleton.name,
                "num_joints": self.config.skeleton.num_joints,
                "num_limbs": self.config.skeleton.num_limbs,
            }
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "project_name": self.config.project_name,
            "num_animals": self.config.num_animals,
            "confidence_threshold": self.config.confidence_threshold,
            **skel_info,
            "components": [
                "HeatmapGenerator", "KeypointDetector", "PAFGenerator",
                "BipartiteMatching", "KalmanTracker", "BehavioralAnalyzer",
                "DataAugmenter", "SkeletonPresets",
            ],
            "presets": ["mouse", "human_coco"],
            "tracker_active_tracks": len([t for t in self.tracker.tracks if t.active]),
            "status": "operational",
        }
