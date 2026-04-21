# ===========================================================================
# OMNI COMPUTE LAYER — PYCAPCUT VIDEO ENGINE
# ===========================================================================
# Source Repo   : github.com/GuanYixuan/pyCapCut
# Domain Layer  : Compute (Media processing, video editing automation)
# Language      : Python
# Function      : Automated video editing pipeline — CapCut draft format
#                 parsing/generation, multi-track timeline (video/audio/text/
#                 sticker/effect), keyframe animation, transition sequencing,
#                 text overlay composition with styles, speed ramping with
#                 curves, audio ducking, batch rendering queue, and template-
#                 based video generation from structured data.
# ===========================================================================

"""
OMNI Pycapcut Engine
====================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
from __future__ import annotations

import json
import time
import uuid
import hashlib
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Any, Optional
from pathlib import Path


ENGINE_VERSION = "1.0.0-omni"


# ---- Track Types -----------------------------------------------------------

class TrackType(Enum):
    """Type enumeration for TrackType."""
    VIDEO = "video"
    AUDIO = "audio"
    TEXT = "text"
    STICKER = "sticker"
    EFFECT = "effect"
    FILTER = "filter"
    TRANSITION = "transition"


# ---- Blend Modes -----------------------------------------------------------

class BlendMode(Enum):
    """Production-grade Blend Mode component."""
    NORMAL = "normal"
    MULTIPLY = "multiply"
    SCREEN = "screen"
    OVERLAY = "overlay"
    SOFT_LIGHT = "soft_light"
    HARD_LIGHT = "hard_light"
    DIFFERENCE = "difference"


# ---- Easing Functions ------------------------------------------------------

class EasingType(Enum):
    """Type enumeration for EasingType."""
    LINEAR = "linear"
    EASE_IN = "ease_in"
    EASE_OUT = "ease_out"
    EASE_IN_OUT = "ease_in_out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"
    BACK = "back"


# ---- Speed Curve Types ----------------------------------------------------

class SpeedCurveType(Enum):
    """Type enumeration for SpeedCurveType."""
    CONSTANT = "constant"
    MONTAGE = "montage"
    HERO_MOMENT = "hero_moment"
    BULLET_TIME = "bullet_time"
    JUMP_CUT = "jump_cut"
    FLASH_IN = "flash_in"
    CUSTOM = "custom"


# ---- Render Quality --------------------------------------------------------

class RenderQuality(IntEnum):
    """Production-grade Render Quality component."""
    DRAFT = 1        # 480p, fast preview
    STANDARD = 2     # 720p
    HIGH = 3         # 1080p
    ULTRA = 4        # 4K
    MAXIMUM = 5      # Original resolution


class RenderFormat(Enum):
    """Production-grade Render Format component."""
    MP4 = "mp4"
    MOV = "mov"
    WEBM = "webm"
    GIF = "gif"


# ---- Keyframe --------------------------------------------------------------

@dataclass
class Keyframe:
    """A single animation keyframe on a property."""
    time_offset_us: int           # Microseconds from segment start
    value: float
    easing: EasingType = EasingType.LINEAR

    def to_dict(self) -> dict:
        """Convert to dict representation."""
        return {
            "time_offset": self.time_offset_us,
            "value": self.value,
            "easing": self.easing.value,
        }


@dataclass
class KeyframeTrack:
    """A track of keyframes for a single animated property."""
    property_name: str            # e.g. "opacity", "scale_x", "rotation"
    keyframes: list[Keyframe] = field(default_factory=list)

    def add(self, time_us: int, value: float, easing: EasingType = EasingType.LINEAR):
        """Execute add operation for KeyframeTrack."""
        self.keyframes.append(Keyframe(time_us, value, easing))
        self.keyframes.sort(key=lambda k: k.time_offset_us)

    def value_at(self, time_us: int) -> float:
        """Interpolate value at given time."""
        if not self.keyframes:
            return 0.0
        if time_us <= self.keyframes[0].time_offset_us:
            return self.keyframes[0].value
        if time_us >= self.keyframes[-1].time_offset_us:
            return self.keyframes[-1].value

        for i in range(len(self.keyframes) - 1):
            k1, k2 = self.keyframes[i], self.keyframes[i + 1]
            if k1.time_offset_us <= time_us <= k2.time_offset_us:
                t = (time_us - k1.time_offset_us) / max(1, k2.time_offset_us - k1.time_offset_us)
                return k1.value + (k2.value - k1.value) * t
        return self.keyframes[-1].value


# ---- Segment (Clip on Timeline) -------------------------------------------

@dataclass
class Segment:
    """A single clip/element on the timeline."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:12])
    track_type: TrackType = TrackType.VIDEO
    source_path: str = ""
    start_time_us: int = 0            # Position on timeline (microseconds)
    duration_us: int = 3_000_000      # Duration on timeline
    source_start_us: int = 0          # Trim start in source
    source_end_us: int = 0            # Trim end in source (0 = full)
    volume: float = 1.0
    opacity: float = 1.0
    speed: float = 1.0
    blend_mode: BlendMode = BlendMode.NORMAL
    position_x: float = 0.0           # -1.0 to 1.0 (normalized)
    position_y: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    rotation: float = 0.0             # Degrees
    flip_horizontal: bool = False
    flip_vertical: bool = False
    animations: list[KeyframeTrack] = field(default_factory=list)
    # Text-specific
    text_content: str = ""
    font_name: str = "Inter"
    font_size: float = 48.0
    font_color: str = "#FFFFFF"
    font_bold: bool = False
    font_italic: bool = False
    text_alignment: str = "center"     # "left", "center", "right"
    text_bg_color: str = ""            # Empty = no background
    text_bg_opacity: float = 0.7
    stroke_color: str = ""
    stroke_width: float = 0.0
    letter_spacing: float = 0.0
    line_height: float = 1.2
    # Effect/filter
    effect_id: str = ""
    effect_params: dict[str, Any] = field(default_factory=dict)

    @property
    def end_time_us(self) -> int:
        """Execute end time us operation for Segment."""
        return self.start_time_us + self.duration_us

    def add_animation(self, prop: str, keyframes: list[tuple[int, float, EasingType]]):
        """Add keyframe animation to a property."""
        track = KeyframeTrack(property_name=prop)
        for time_us, value, easing in keyframes:
            track.add(time_us, value, easing)
        self.animations.append(track)

    def to_dict(self) -> dict:
        """Convert to dict representation."""
        d = {
            "id": self.id,
            "type": self.track_type.value,
            "source": self.source_path,
            "timeline_start": self.start_time_us,
            "duration": self.duration_us,
            "source_start": self.source_start_us,
            "source_end": self.source_end_us,
            "volume": self.volume,
            "opacity": self.opacity,
            "speed": self.speed,
            "blend_mode": self.blend_mode.value,
            "transform": {
                "x": self.position_x,
                "y": self.position_y,
                "scale_x": self.scale_x,
                "scale_y": self.scale_y,
                "rotation": self.rotation,
            },
            "animations": [
                {"property": a.property_name, "keyframes": [k.to_dict() for k in a.keyframes]}
                for a in self.animations
            ],
        }
        if self.track_type == TrackType.TEXT:
            d["text"] = {
                "content": self.text_content,
                "font": self.font_name,
                "size": self.font_size,
                "color": self.font_color,
                "bold": self.font_bold,
                "italic": self.font_italic,
                "alignment": self.text_alignment,
                "bg_color": self.text_bg_color,
                "bg_opacity": self.text_bg_opacity,
                "stroke_color": self.stroke_color,
                "stroke_width": self.stroke_width,
                "letter_spacing": self.letter_spacing,
                "line_height": self.line_height,
            }
        return d


# ---- Transition ------------------------------------------------------------

@dataclass
class Transition:
    """A transition between two adjacent segments."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = "fade"
    duration_us: int = 500_000       # 0.5 seconds
    resource_id: str = ""            # CapCut transition resource ID

    def to_dict(self) -> dict:
        """Convert to dict representation."""
        return {
            "id": self.id,
            "name": self.name,
            "duration": self.duration_us,
            "resource_id": self.resource_id,
        }


# ---- Speed Ramp -----------------------------------------------------------

@dataclass
class SpeedRamp:
    """Speed ramping curve for a video segment."""
    curve_type: SpeedCurveType = SpeedCurveType.CONSTANT
    points: list[tuple[float, float]] = field(default_factory=list)
    # points: list of (normalized_time 0-1, speed_multiplier)

    @classmethod
    def montage(cls) -> SpeedRamp:
        """Execute montage operation for SpeedRamp."""
        return cls(
            curve_type=SpeedCurveType.MONTAGE,
            points=[(0.0, 1.0), (0.2, 2.0), (0.4, 0.5), (0.6, 2.5), (0.8, 0.3), (1.0, 1.0)]
        )

    @classmethod
    def hero_moment(cls) -> SpeedRamp:
        """Execute hero moment operation for SpeedRamp."""
        return cls(
            curve_type=SpeedCurveType.HERO_MOMENT,
            points=[(0.0, 1.0), (0.3, 1.0), (0.4, 0.2), (0.6, 0.2), (0.7, 1.0), (1.0, 1.0)]
        )

    @classmethod
    def bullet_time(cls) -> SpeedRamp:
        """Execute bullet time operation for SpeedRamp."""
        return cls(
            curve_type=SpeedCurveType.BULLET_TIME,
            points=[(0.0, 1.5), (0.2, 0.1), (0.5, 0.05), (0.8, 0.1), (1.0, 1.5)]
        )

    def speed_at(self, t: float) -> float:
        """Get speed multiplier at normalized time t (0-1)."""
        if not self.points:
            return 1.0
        if t <= self.points[0][0]:
            return self.points[0][1]
        if t >= self.points[-1][0]:
            return self.points[-1][1]
        for i in range(len(self.points) - 1):
            t1, s1 = self.points[i]
            t2, s2 = self.points[i + 1]
            if t1 <= t <= t2:
                ratio = (t - t1) / max(0.001, t2 - t1)
                return s1 + (s2 - s1) * ratio
        return 1.0


# ---- Track -----------------------------------------------------------------

@dataclass
class Track:
    """A single track (layer) on the timeline."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    track_type: TrackType = TrackType.VIDEO
    name: str = ""
    segments: list[Segment] = field(default_factory=list)
    transitions: list[Transition] = field(default_factory=list)
    muted: bool = False
    locked: bool = False
    visible: bool = True

    @property
    def duration_us(self) -> int:
        """Execute duration us operation for Track."""
        if not self.segments:
            return 0
        return max(s.end_time_us for s in self.segments)

    def add_segment(self, segment: Segment) -> Segment:
        """Add segment to Track."""
        segment.track_type = self.track_type
        self.segments.append(segment)
        self.segments.sort(key=lambda s: s.start_time_us)
        return segment

    def add_transition(self, transition: Transition, after_index: int = -1):
        """Add transition to Track."""
        self.transitions.append(transition)


# ---- Project ---------------------------------------------------------------

@dataclass
class CapCutProject:
    """A complete CapCut project containing tracks and metadata."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Untitled Project"
    resolution_w: int = 1920
    resolution_h: int = 1080
    fps: float = 30.0
    tracks: list[Track] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    @property
    def duration_us(self) -> int:
        """Execute duration us operation for CapCutProject."""
        if not self.tracks:
            return 0
        return max(t.duration_us for t in self.tracks)

    @property
    def duration_seconds(self) -> float:
        """Execute duration seconds operation for CapCutProject."""
        return self.duration_us / 1_000_000

    @property
    def total_segments(self) -> int:
        """Execute total segments operation for CapCutProject."""
        return sum(len(t.segments) for t in self.tracks)

    def add_video_track(self, name: str = "") -> Track:
        """Add video track to CapCutProject."""
        track = Track(track_type=TrackType.VIDEO, name=name or f"Video {len(self.tracks) + 1}")
        self.tracks.append(track)
        return track

    def add_audio_track(self, name: str = "") -> Track:
        """Add audio track to CapCutProject."""
        track = Track(track_type=TrackType.AUDIO, name=name or f"Audio {len(self.tracks) + 1}")
        self.tracks.append(track)
        return track

    def add_text_track(self, name: str = "") -> Track:
        """Add text track to CapCutProject."""
        track = Track(track_type=TrackType.TEXT, name=name or f"Text {len(self.tracks) + 1}")
        self.tracks.append(track)
        return track

    def add_effect_track(self, name: str = "") -> Track:
        """Add effect track to CapCutProject."""
        track = Track(track_type=TrackType.EFFECT, name=name or f"Effect {len(self.tracks) + 1}")
        self.tracks.append(track)
        return track

    def to_dict(self) -> dict:
        """Convert to dict representation."""
        return {
            "id": self.id,
            "name": self.name,
            "canvas": {
                "width": self.resolution_w,
                "height": self.resolution_h,
                "fps": self.fps,
            },
            "duration_us": self.duration_us,
            "duration_seconds": self.duration_seconds,
            "total_segments": self.total_segments,
            "tracks": [
                {
                    "id": t.id,
                    "type": t.track_type.value,
                    "name": t.name,
                    "segments": [s.to_dict() for s in t.segments],
                    "transitions": [tr.to_dict() for tr in t.transitions],
                    "muted": t.muted,
                    "locked": t.locked,
                }
                for t in self.tracks
            ],
        }


# ---- Render Job ------------------------------------------------------------

@dataclass
class RenderJob:
    """A batch render job."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    project_id: str = ""
    output_path: str = ""
    quality: RenderQuality = RenderQuality.HIGH
    fmt: RenderFormat = RenderFormat.MP4
    status: str = "pending"    # pending, rendering, complete, failed
    progress: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0
    error: str = ""
    output_size_bytes: int = 0


# ---- Video Template --------------------------------------------------------

@dataclass
class VideoTemplate:
    """A reusable video template for batch generation."""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    description: str = ""
    resolution_w: int = 1920
    resolution_h: int = 1080
    fps: float = 30.0
    segments_schema: list[dict[str, Any]] = field(default_factory=list)
    # segments_schema defines slots: [{"type": "video", "duration_us": 3000000}, ...]
    text_slots: list[dict[str, str]] = field(default_factory=list)
    # text_slots: [{"key": "title", "default": "My Title", "position": "center"}, ...]
    transitions_default: str = "fade"
    bgm_path: str = ""


# ---- OmniPyCapCutEngine (Main) --------------------------------------------

class OmniPyCapCutEngine:
    """
    OMNI pyCapCut Engine — automated video editing pipeline.

    Capabilities:
    - Parse/generate CapCut draft JSON format
    - Multi-track timeline editing (video/audio/text/sticker/effect)
    - Keyframe-based property animation
    - Transition sequencing between clips
    - Text overlay composition with rich styling
    - Speed ramping with preset/custom curves
    - Audio ducking (auto-lower music during voice)
    - Batch rendering queue
    - Template-based video generation from structured data
    """

    def __init__(self, workspace_dir: str = ".pycapcut"):
        """Initialize OmniPyCapCutEngine."""
        self.workspace = Path(workspace_dir)
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.projects: dict[str, CapCutProject] = {}
        self.templates: dict[str, VideoTemplate] = {}
        self.render_queue: list[RenderJob] = []
        self.speed_presets: dict[str, SpeedRamp] = {
            "montage": SpeedRamp.montage(),
            "hero_moment": SpeedRamp.hero_moment(),
            "bullet_time": SpeedRamp.bullet_time(),
        }
        print(f"[PYCAPCUT-OMNI-PY] Video engine initialized: workspace={self.workspace}")

    # ---- Project Management ------------------------------------------------

    def create_project(
        self,
        name: str,
        width: int = 1920,
        height: int = 1080,
        fps: float = 30.0,
    ) -> CapCutProject:
        """Create a new video project."""
        project = CapCutProject(
            name=name,
            resolution_w=width,
            resolution_h=height,
            fps=fps,
        )
        self.projects[project.id] = project
        print(f"[PYCAPCUT-OMNI-PY] Project created: '{name}' ({width}x{height} @ {fps}fps)")
        return project

    def get_project(self, project_id: str) -> Optional[CapCutProject]:
        """Performs get project operation for OmniPyCapCutEngine."""
        return self.projects.get(project_id)

    def list_projects(self) -> list[dict[str, Any]]:
        """Performs list projects operation for OmniPyCapCutEngine."""
        return [
            {
                "id": p.id,
                "name": p.name,
                "resolution": f"{p.resolution_w}x{p.resolution_h}",
                "duration_s": round(p.duration_seconds, 2),
                "segments": p.total_segments,
                "tracks": len(p.tracks),
            }
            for p in self.projects.values()
        ]

    # ---- Track Operations --------------------------------------------------

    def add_video_clip(
        self,
        project_id: str,
        source_path: str,
        start_us: int = 0,
        duration_us: int = 3_000_000,
        track_index: int = 0,
    ) -> Optional[Segment]:
        """Add a video clip to the project timeline."""
        project = self.projects.get(project_id)
        if not project:
            return None

        while len(project.tracks) <= track_index:
            project.add_video_track()

        seg = Segment(
            track_type=TrackType.VIDEO,
            source_path=source_path,
            start_time_us=start_us,
            duration_us=duration_us,
        )
        project.tracks[track_index].add_segment(seg)
        project.updated_at = time.time()
        print(f"[PYCAPCUT-OMNI-PY] Video clip added: {source_path} at {start_us / 1e6:.2f}s")
        return seg

    def add_audio_clip(
        self,
        project_id: str,
        source_path: str,
        start_us: int = 0,
        duration_us: int = 5_000_000,
        volume: float = 1.0,
    ) -> Optional[Segment]:
        """Add an audio clip to the project."""
        project = self.projects.get(project_id)
        if not project:
            return None

        audio_track = None
        for t in project.tracks:
            if t.track_type == TrackType.AUDIO:
                audio_track = t
                break
        if not audio_track:
            audio_track = project.add_audio_track()

        seg = Segment(
            track_type=TrackType.AUDIO,
            source_path=source_path,
            start_time_us=start_us,
            duration_us=duration_us,
            volume=volume,
        )
        audio_track.add_segment(seg)
        project.updated_at = time.time()
        print(f"[PYCAPCUT-OMNI-PY] Audio clip added: {source_path} vol={volume}")
        return seg

    def add_text_overlay(
        self,
        project_id: str,
        text: str,
        start_us: int = 0,
        duration_us: int = 2_000_000,
        font: str = "Inter",
        size: float = 48.0,
        color: str = "#FFFFFF",
        position: tuple[float, float] = (0.0, 0.0),
        bold: bool = False,
    ) -> Optional[Segment]:
        """Add a text overlay to the project."""
        project = self.projects.get(project_id)
        if not project:
            return None

        text_track = None
        for t in project.tracks:
            if t.track_type == TrackType.TEXT:
                text_track = t
                break
        if not text_track:
            text_track = project.add_text_track()

        seg = Segment(
            track_type=TrackType.TEXT,
            start_time_us=start_us,
            duration_us=duration_us,
            text_content=text,
            font_name=font,
            font_size=size,
            font_color=color,
            font_bold=bold,
            position_x=position[0],
            position_y=position[1],
        )
        text_track.add_segment(seg)
        project.updated_at = time.time()
        print(f"[PYCAPCUT-OMNI-PY] Text overlay added: '{text[:30]}...' at {start_us / 1e6:.2f}s")
        return seg

    # ---- Transitions -------------------------------------------------------

    def add_transition(
        self,
        project_id: str,
        track_index: int,
        after_segment_index: int,
        name: str = "fade",
        duration_us: int = 500_000,
    ) -> Optional[Transition]:
        """Add a transition between segments."""
        project = self.projects.get(project_id)
        if not project or track_index >= len(project.tracks):
            return None

        trans = Transition(name=name, duration_us=duration_us)
        project.tracks[track_index].add_transition(trans, after_segment_index)
        print(f"[PYCAPCUT-OMNI-PY] Transition added: {name} ({duration_us / 1e6:.2f}s)")
        return trans

    # ---- Speed Ramping -----------------------------------------------------

    def apply_speed_ramp(
        self,
        project_id: str,
        segment_id: str,
        preset: str = "montage",
    ) -> bool:
        """Apply a speed ramp preset to a segment."""
        project = self.projects.get(project_id)
        if not project:
            return False

        ramp = self.speed_presets.get(preset)
        if not ramp:
            return False

        for track in project.tracks:
            for seg in track.segments:
                if seg.id == segment_id:
                    kf_track = KeyframeTrack(property_name="speed")
                    for t_norm, speed in ramp.points:
                        time_us = int(t_norm * seg.duration_us)
                        kf_track.add(time_us, speed, EasingType.EASE_IN_OUT)
                    seg.animations.append(kf_track)
                    print(f"[PYCAPCUT-OMNI-PY] Speed ramp '{preset}' applied to {segment_id}")
                    return True
        return False

    # ---- Audio Ducking -----------------------------------------------------

    def apply_audio_ducking(
        self,
        project_id: str,
        voice_threshold: float = 0.3,
        duck_level: float = 0.15,
    ) -> int:
        """
        Auto-duck background music when voice is detected.
        Returns number of ducking points created.
        """
        project = self.projects.get(project_id)
        if not project:
            return 0

        voice_segments: list[Segment] = []
        music_segments: list[Segment] = []

        for track in project.tracks:
            for seg in track.segments:
                if seg.track_type == TrackType.AUDIO:
                    if seg.volume >= voice_threshold:
                        voice_segments.append(seg)
                    else:
                        music_segments.append(seg)

        duck_points = 0
        for music in music_segments:
            kf_track = KeyframeTrack(property_name="volume")
            for voice in voice_segments:
                overlap_start = max(music.start_time_us, voice.start_time_us)
                overlap_end = min(music.end_time_us, voice.end_time_us)
                if overlap_start < overlap_end:
                    fade_in = 200_000   # 200ms fade
                    kf_track.add(overlap_start - fade_in, music.volume, EasingType.EASE_OUT)
                    kf_track.add(overlap_start, duck_level, EasingType.EASE_IN)
                    kf_track.add(overlap_end, duck_level, EasingType.EASE_OUT)
                    kf_track.add(overlap_end + fade_in, music.volume, EasingType.EASE_IN)
                    duck_points += 2
            if kf_track.keyframes:
                music.animations.append(kf_track)

        print(f"[PYCAPCUT-OMNI-PY] Audio ducking applied: {duck_points} duck points")
        return duck_points

    # ---- Keyframe Animation ------------------------------------------------

    def animate_segment(
        self,
        project_id: str,
        segment_id: str,
        prop: str,
        keyframes: list[tuple[int, float]],
        easing: EasingType = EasingType.EASE_IN_OUT,
    ) -> bool:
        """Add keyframe animation to a segment property."""
        project = self.projects.get(project_id)
        if not project:
            return False

        for track in project.tracks:
            for seg in track.segments:
                if seg.id == segment_id:
                    kf_list = [(t, v, easing) for t, v in keyframes]
                    seg.add_animation(prop, kf_list)
                    print(f"[PYCAPCUT-OMNI-PY] Animation on '{prop}': "
                          f"{len(keyframes)} keyframes on {segment_id}")
                    return True
        return False

    # ---- Template System ---------------------------------------------------

    def register_template(self, template: VideoTemplate):
        """Register a reusable video template."""
        self.templates[template.id] = template
        print(f"[PYCAPCUT-OMNI-PY] Template registered: '{template.name}' ({template.id})")

    def generate_from_template(
        self,
        template_id: str,
        data: dict[str, Any],
        project_name: str = "",
    ) -> Optional[CapCutProject]:
        """Generate a project from a template with data binding."""
        template = self.templates.get(template_id)
        if not template:
            return None

        project = self.create_project(
            name=project_name or f"From {template.name}",
            width=template.resolution_w,
            height=template.resolution_h,
            fps=template.fps,
        )

        # Create video track and fill slot segments
        video_track = project.add_video_track("Main Video")
        cursor_us = 0
        for slot in template.segments_schema:
            source = data.get(slot.get("data_key", ""), slot.get("default_source", ""))
            dur = slot.get("duration_us", 3_000_000)
            seg = Segment(
                track_type=TrackType.VIDEO,
                source_path=source,
                start_time_us=cursor_us,
                duration_us=dur,
            )
            video_track.add_segment(seg)
            cursor_us += dur

        # Fill text slots
        text_track = project.add_text_track("Text Overlay")
        for slot in template.text_slots:
            key = slot.get("key", "")
            text = data.get(key, slot.get("default", ""))
            start = slot.get("start_us", 0)
            dur = slot.get("duration_us", 2_000_000)
            seg = Segment(
                track_type=TrackType.TEXT,
                text_content=text,
                start_time_us=start,
                duration_us=dur,
                font_size=float(slot.get("font_size", 48)),
                font_color=slot.get("color", "#FFFFFF"),
            )
            text_track.add_segment(seg)

        # Add BGM if specified
        if template.bgm_path:
            self.add_audio_clip(project.id, template.bgm_path, 0, cursor_us, volume=0.3)

        print(f"[PYCAPCUT-OMNI-PY] Project generated from template '{template.name}': "
              f"{project.total_segments} segments, {project.duration_seconds:.1f}s")
        return project

    # ---- Render Queue ------------------------------------------------------

    def enqueue_render(
        self,
        project_id: str,
        output_path: str,
        quality: RenderQuality = RenderQuality.HIGH,
        fmt: RenderFormat = RenderFormat.MP4,
    ) -> Optional[RenderJob]:
        """Add a render job to the queue."""
        project = self.projects.get(project_id)
        if not project:
            return None

        job = RenderJob(
            project_id=project_id,
            output_path=output_path,
            quality=quality,
            fmt=fmt,
        )
        self.render_queue.append(job)
        print(f"[PYCAPCUT-OMNI-PY] Render enqueued: {output_path} "
              f"({quality.name}, {fmt.value})")
        return job

    def process_render_queue(self) -> list[dict[str, Any]]:
        """Process all pending render jobs."""
        results = []
        for job in self.render_queue:
            if job.status != "pending":
                continue

            job.status = "rendering"
            job.started_at = time.time()
            project = self.projects.get(job.project_id)

            if not project:
                job.status = "failed"
                job.error = "Project not found"
                continue

            # Real: invoke FFmpeg pipeline with project timeline
            # Here: simulate rendering progression
            print(f"[PYCAPCUT-OMNI-PY] Rendering: {project.name} -> {job.output_path}")
            job.progress = 1.0
            job.status = "complete"
            job.completed_at = time.time()

            results.append({
                "job_id": job.id,
                "project": project.name,
                "output": job.output_path,
                "quality": job.quality.name,
                "duration_s": round(project.duration_seconds, 2),
                "render_time_s": round(job.completed_at - job.started_at, 2),
            })

        return results

    # ---- Export/Import Draft Format -----------------------------------------

    def export_draft(self, project_id: str) -> Optional[str]:
        """Export project as CapCut-compatible draft JSON."""
        project = self.projects.get(project_id)
        if not project:
            return None

        draft = {
            "type": "draft_content",
            "version": ENGINE_VERSION,
            "id": project.id,
            "name": project.name,
            "canvas_config": {
                "width": project.resolution_w,
                "height": project.resolution_h,
                "ratio": f"{project.resolution_w}:{project.resolution_h}",
                "fps": project.fps,
            },
            "duration": project.duration_us,
            "tracks": project.to_dict()["tracks"],
            "created_at": project.created_at,
            "updated_at": time.time(),
        }

        output_path = self.workspace / f"{project.id}_draft.json"
        output_path.write_text(json.dumps(draft, indent=2), encoding="utf-8")
        print(f"[PYCAPCUT-OMNI-PY] Draft exported: {output_path}")
        return str(output_path)

    def import_draft(self, draft_path: str) -> Optional[CapCutProject]:
        """Import a CapCut draft JSON into a project."""
        path = Path(draft_path)
        if not path.exists():
            return None

        data = json.loads(path.read_text(encoding="utf-8"))
        canvas = data.get("canvas_config", {})
        project = self.create_project(
            name=data.get("name", "Imported"),
            width=canvas.get("width", 1920),
            height=canvas.get("height", 1080),
            fps=canvas.get("fps", 30.0),
        )

        tracks_data = data.get("tracks", [])
        for td in tracks_data:
            track_type = TrackType(td.get("type", "video"))
            track = Track(track_type=track_type, name=td.get("name", ""))
            for sd in td.get("segments", []):
                seg = Segment(
                    track_type=track_type,
                    source_path=sd.get("source", ""),
                    start_time_us=sd.get("timeline_start", 0),
                    duration_us=sd.get("duration", 3_000_000),
                )
                if track_type == TrackType.TEXT and "text" in sd:
                    text_data = sd["text"]
                    seg.text_content = text_data.get("content", "")
                    seg.font_name = text_data.get("font", "Inter")
                    seg.font_size = text_data.get("size", 48.0)
                    seg.font_color = text_data.get("color", "#FFFFFF")
                track.add_segment(seg)
            project.tracks.append(track)

        print(f"[PYCAPCUT-OMNI-PY] Draft imported: '{project.name}' "
              f"({project.total_segments} segments)")
        return project

    # ---- Diagnostics -------------------------------------------------------

    def diagnostics(self) -> dict[str, Any]:
        """Performs diagnostics operation for OmniPyCapCutEngine."""
        return {
            "engine": "OmniPyCapCutEngine",
            "version": ENGINE_VERSION,
            "projects": len(self.projects),
            "templates": len(self.templates),
            "render_queue": len(self.render_queue),
            "speed_presets": list(self.speed_presets.keys()),
            "workspace": str(self.workspace),
            "total_segments": sum(p.total_segments for p in self.projects.values()),
            "total_duration_s": round(
                sum(p.duration_seconds for p in self.projects.values()), 2
            ),
        }
