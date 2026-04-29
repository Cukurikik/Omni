# Omni Music Generation Engine
# Ref: shaopengw/Awesome-Music-Generation
from typing import List, Dict
import math

def calculate_melody_smoothness(pitch_sequence: List[int]) -> float:
    """Calculate the smoothness of a generated melody sequence (lower variance in intervals = smoother)."""
    if len(pitch_sequence) < 2:
        return 1.0
        
    intervals = [abs(pitch_sequence[i] - pitch_sequence[i-1]) for i in range(1, len(pitch_sequence))]
    mean_interval = sum(intervals) / len(intervals)
    
    variance = sum((i - mean_interval)**2 for i in intervals) / len(intervals)
    return round(1.0 / (1.0 + math.sqrt(variance)), 4)

def rhythm_consistency_score(durations: List[float], expected_beat: float = 1.0) -> float:
    """Calculate how consistently notes align with an expected beat."""
    if not durations:
        return 0.0
        
    deviations = [abs((d % expected_beat) - (expected_beat / 2)) for d in durations]
    # Lower deviation from grid points (0 or expected_beat) is better
    avg_deviation = sum(min(d, expected_beat - d) for d in deviations) / len(durations)
    return round(1.0 - (avg_deviation / (expected_beat / 2)), 4)

def evaluate_music_generation(pitches: List[int], durations: List[float]) -> Dict[str, float]:
    return {
        "melody_smoothness": calculate_melody_smoothness(pitches),
        "rhythm_consistency": rhythm_consistency_score(durations),
        "total_notes": float(len(pitches))
    }
