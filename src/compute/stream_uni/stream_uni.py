import math
import numpy as np
from typing import Tuple, Optional, Dict, Any

class StreamUniComputeError(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)
        self.msg = msg

class Result:
    def __init__(self, value: Optional[Any], error: Optional[StreamUniComputeError] = None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> Any:
        if not self.is_ok():
            raise self.error
        return self.value

class StreamUniEngine:
    """
    OMNI Engine: StreamUni
    Calculates universal bit-rate vectors and structural integrity mappings for generalized media streaming.
    """
    def __init__(self, max_buffer_size: int = 2048):
        self.max_buffer_size = max_buffer_size

    def calculate_bitrate_adaptation(self, bandwidth_trace: np.ndarray, current_buffer: float) -> Result:
        try:
            if not isinstance(bandwidth_trace, np.ndarray):
                return Result(None, StreamUniComputeError("Bandwidth trace must be np.ndarray"))
            if current_buffer < 0.0:
                return Result(None, StreamUniComputeError("Buffer cannot be mathematically negative"))
                
            harmonic_mean_bw = float(len(bandwidth_trace) / np.sum(1.0 / (bandwidth_trace + 1e-9)))
            
            # Lyapunov optimization logic constraint
            v_param = 0.5
            penalty = max(0.0, self.max_buffer_size - current_buffer)
            
            optimal_bitrate = harmonic_mean_bw * (1.0 - (v_param / (penalty + 1.0)))
            optimal_bitrate = max(0.1, optimal_bitrate) # Min floor limit
            
            return Result({'optimal_bitrate': optimal_bitrate, 'harmonic_bw': harmonic_mean_bw})
        except Exception as e:
            return Result(None, StreamUniComputeError(f"Bitrate adaptation failed: {str(e)}"))

    def compute_packet_loss_geometry(self, received_seqs: np.ndarray, expected_total: int) -> Result:
        try:
            if expected_total <= 0:
                return Result(None, StreamUniComputeError("Expected total must be > 0"))
                
            actual_received = len(np.unique(received_seqs))
            loss_ratio = 1.0 - (float(actual_received) / float(expected_total))
            
            if loss_ratio < 0.0:
                return Result(None, StreamUniComputeError("Loss ratio mathematical impossibility: > 100% received limit"))
                
            return Result({'loss_ratio': float(loss_ratio), 'received': actual_received})
        except Exception as e:
            return Result(None, StreamUniComputeError(f"Packet loss computation failed: {str(e)}"))
