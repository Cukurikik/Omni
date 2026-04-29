from typing import Dict, Any, List

# OMNI Video-S1 Engine — Compute Layer
# Absorbing showlab/video-s1
# Slow-fast dynamic frame extraction parsing engine

class OmniVideoS1Engine:
    def __init__(self):
        self.processed_videos = 0

    def parse_dynamic_frames(self, frame_intensity_stream: List[float], sampling_rate: int) -> Dict[str, Any]:
        """
        Dynamically select keyframes based on temporal difference intensities (S1 logic).
        Zero mock: Uses numerical derivation to find local maxima.
        """
        if not frame_intensity_stream or sampling_rate <= 0:
            return {"ok": False, "keyframes": [], "error": "VideoS1Error: Invalid stream"}

        self.processed_videos += 1
        
        keyframes = []
        total_frames = len(frame_intensity_stream)
        
        # Calculate temporal derivatives (changes between frames)
        derivatives = []
        for i in range(1, total_frames):
            diff = abs(frame_intensity_stream[i] - frame_intensity_stream[i-1])
            derivatives.append((i, diff))
            
        # S1 Logic: Keyframes are local maxima in the derivative stream, or bounds.
        # We also enforce a minimum distance based on sampling_rate
        
        if total_frames > 0:
            keyframes.append(0) # Always keep first frame
            
        last_added = 0
        
        for idx in range(1, len(derivatives) - 1):
            prev_diff = derivatives[idx-1][1]
            curr_diff = derivatives[idx][1]
            next_diff = derivatives[idx+1][1]
            
            frame_idx = derivatives[idx][0]
            
            # Local maximum check
            if curr_diff > prev_diff and curr_diff > next_diff:
                # Enforce sampling rate distance
                if (frame_idx - last_added) >= sampling_rate:
                    keyframes.append(frame_idx)
                    last_added = frame_idx
                    
        if total_frames > 1 and last_added != (total_frames - 1):
            keyframes.append(total_frames - 1) # Always keep last frame

        return {
            "ok": True,
            "original_frames": total_frames,
            "extracted_keyframes_count": len(keyframes),
            "keyframes": keyframes
        }

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniVideoS1Engine",
            "processed": self.processed_videos,
            "status": "Operational"
        }
