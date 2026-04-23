from __future__ import annotations
from typing import Dict, Any, List, Tuple
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniVideoEditorTimelineEngine:
    """
    omni-video-editor-timeline
    
    A native boundary structural engine computing overlapping 1D video timeline intersections.
    Calculates occlusion limits, track visibility frames, and overlapping metrics natively.
    Inspired by nobleosinachi.github.io.
    """
    
    ENGINE_VERSION = "omni-s11-b4.1.0"
    
    def __init__(self) -> None:
        pass

    def calculate_occluded_intervals(self, video_tracks: List[Tuple[int, int, int]]) -> Result:
        """
        video_tracks formatted as: [(z_index, frame_start, frame_end), ...]
        Higher z_index implies occlusion over lower z_index boundaries.
        Returns actual visible frames for each track.
        """
        try:
            if not video_tracks:
                return Err(ValueError("No valid video tracks loaded for interval checking."))
                
            for struct in video_tracks:
                if struct[1] >= struct[2]:
                    return Err(ValueError(f"Invalid frame duration structure detected at z-index {struct[0]}"))
            
            # Sort tracks by Z-Index ascending natively
            sorted_tracks = sorted(video_tracks, key=lambda t: t[0])
            
            visible_segments = {} # z_index -> list of (start, end)
            
            # For each track, check what part of it is occluded by tracks situated ABOVE it
            for i, (current_z, cur_start, cur_end) in enumerate(sorted_tracks):
                
                # Initially the entire track is visible
                current_visible = [(cur_start, cur_end)]
                
                # Check against all tracks positioned above it
                for j in range(i + 1, len(sorted_tracks)):
                    higher_z, h_start, h_end = sorted_tracks[j]
                    
                    new_visible = []
                    for v_start, v_end in current_visible:
                        # Find intersection logic (1D slice math)
                        intersect_start = max(v_start, h_start)
                        intersect_end = min(v_end, h_end)
                        
                        if intersect_start < intersect_end:
                            # It is eclipsed, we must fragment the interval
                            if v_start < intersect_start:
                                new_visible.append((v_start, intersect_start))
                            if intersect_end < v_end:
                                new_visible.append((intersect_end, v_end))
                        else:
                            # No eclipse boundaries
                            new_visible.append((v_start, v_end))
                            
                    current_visible = new_visible
                
                # Accumulate the total visible frames structurally
                total_visible_frames = sum((e - s) for s, e in current_visible)
                visible_segments[current_z] = {
                    "intervals": current_visible,
                    "visible_duration": total_visible_frames,
                    "original_duration": cur_end - cur_start,
                    "is_completely_eclipsed": total_visible_frames == 0
                }
                
            return Ok({"visibility_matrix": visible_segments})
            
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """System bounds diagnostics."""
        return {
            "engine": "OmniVideoEditorTimelineEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "complexity": "O(N^2) 1D Spatial Bounds Math"
        }
