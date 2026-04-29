# ShareGPT4Video — Video Frame Sampler & Caption Pipeline
import torch
from typing import Optional, Generic, TypeVar, List
T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class VideoFrameSampler:
    MAX_FRAMES = 256; MAX_RES = 1080; MAX_DURATION_S = 3600
    def sample_uniform(self, total_frames: int, num_samples: int) -> OmniResult[List[int], str]:
        if total_frames <= 0: return OmniResult(error="Zero frames")
        if num_samples > self.MAX_FRAMES: return OmniResult(error=f"Samples exceed {self.MAX_FRAMES}")
        if num_samples > total_frames: num_samples = total_frames
        step = total_frames / num_samples
        indices = [int(i * step) for i in range(num_samples)]
        return OmniResult(value=indices)
