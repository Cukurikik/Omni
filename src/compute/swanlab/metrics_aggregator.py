import numpy as np
from typing import List, Dict, Tuple, Optional

# OMNI SWANLAB: Metrics Aggregator
# Python logic to aggregate and smooth training metrics (loss, accuracy) over time.
# Source: SwanHubX/SwanLab

class MetricsAggregatorError(Exception):
    pass

class MetricsAggregator:
    @staticmethod
    def smooth_exponential_moving_average(
        scalars: List[float], 
        weight: float = 0.8
    ) -> Tuple[Optional[List[float]], Optional[MetricsAggregatorError]]:
        """
        Applies Exponential Moving Average (EMA) smoothing to a series of scalars.
        Used heavily in TensorBoard and SwanLab for loss curve visualization.
        """
        try:
            if not scalars:
                return [], None
            
            if not (0.0 <= weight <= 1.0):
                return None, MetricsAggregatorError("Weight must be between 0.0 and 1.0")

            smoothed = []
            last = scalars[0]
            
            for point in scalars:
                if np.isnan(point) or np.isinf(point):
                    smoothed.append(point)
                    last = point
                else:
                    smoothed_val = last * weight + (1 - weight) * point
                    smoothed.append(smoothed_val)
                    last = smoothed_val
                    
            return smoothed, None
        except Exception as e:
            return None, MetricsAggregatorError(f"EMA smoothing failed: {str(e)}")

    @staticmethod
    def downsample(
        steps: List[int], 
        scalars: List[float], 
        max_points: int = 1000
    ) -> Tuple[Optional[Tuple[List[int], List[float]]], Optional[MetricsAggregatorError]]:
        """
        Downsamples high-frequency metrics to max_points using uniform sampling
        to prevent browser UI lag on huge training runs.
        """
        try:
            if len(scalars) != len(steps):
                return None, MetricsAggregatorError("Steps and scalars must be same length")
                
            if len(scalars) <= max_points:
                return (steps, scalars), None

            # Calculate downsample factor
            indices = np.linspace(0, len(scalars) - 1, max_points, dtype=int)
            
            sampled_steps = [steps[i] for i in indices]
            sampled_scalars = [scalars[i] for i in indices]
            
            return (sampled_steps, sampled_scalars), None
        except Exception as e:
            return None, MetricsAggregatorError(f"Downsampling failed: {str(e)}")
