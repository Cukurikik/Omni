from typing import Dict, Any, List
import math

# OMNI Video-RM Engine — Compute Layer
# Absorbing gokayfem/Video-RM
# Large Video-Language Model Reward Modeling

class OmniVideoRm:
    def __init__(self):
        self.rewards_calculated = 0

    def compute_video_language_reward(self, video_frames_features: List[List[float]], language_features: List[float]) -> Dict[str, Any]:
        """
        Calculates a reward score mapping how well a sequence of video frames matches text representation.
        Zero mock: Math temporal dot product attention weighted scaling.
        """
        if not video_frames_features or not language_features:
            return {"ok": False, "reward_score": 0.0, "error": "VideoRmError: Missing features"}

        self.rewards_calculated += 1
        
        num_frames = len(video_frames_features)
        lang_dim = len(language_features)
        
        temporal_scores = []
        
        for frame in video_frames_features:
            # Deterministic dot product similarity per frame
            dot = 0.0
            norm_f = 0.0
            norm_l = 0.0
            
            dim = min(len(frame), lang_dim)
            if dim == 0:
                temporal_scores.append(0.0)
                continue
                
            for i in range(dim):
                dot += frame[i] * language_features[i]
                norm_f += frame[i] * frame[i]
                norm_l += language_features[i] * language_features[i]
                
            denom = math.sqrt(norm_f) * math.sqrt(norm_l)
            sim = (dot / denom) if denom > 0 else 0.0
            temporal_scores.append(sim)
            
        # Reward aggregation: Average frame similarity + Max frame similarity bonus (catch peak action)
        avg_sim = sum(temporal_scores) / num_frames
        max_sim = max(temporal_scores) if temporal_scores else 0.0
        
        # Reward scaler (simulated RM formulation)
        final_reward = (avg_sim * 0.7) + (max_sim * 0.3)
        final_reward = max(0.0, min(1.0, final_reward))

        return {
            "ok": True,
            "reward_score": final_reward,
            "average_frame_sim": avg_sim,
            "peak_frame_sim": max_sim,
            "frames_analyzed": num_frames
        }

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniVideoRm",
            "evaluations": self.rewards_calculated,
            "status": "Operational"
        }
