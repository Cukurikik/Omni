from typing import List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result, Ok, Err

class OmniTimeSeriesForecastingEngine(OmniBaseEngine):
    """Production-grade Omni Time Series Forecasting Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def extrapolate_linear_trend(self, data_points: List[float], periods: int) -> Result[List[float], str]:
        """Perform extrapolate linear trend computation.

            Args:
                    data_points: List[float]
                    periods: int

            Returns:
                Result: Monadic result wrapping the computed value or error.
            """
        if not data_points:
            return Err("Datapoints cannot be empty.")
        if periods <= 0:
            return Err("Periods must be positive.")
        if len(data_points) < 2:
            return Err("Need at least two data points for a trend.")
            
        n = len(data_points)
        x_sum = sum(range(n))
        y_sum = sum(data_points)
        xy_sum = sum(i * y for i, y in enumerate(data_points))
        x_sq_sum = sum(i ** 2 for i in range(n))
        
        denominator = (n * x_sq_sum - x_sum ** 2)
        if denominator == 0:
            slope = 0.0
        else:
            slope = (n * xy_sum - x_sum * y_sum) / float(denominator)
            
        intercept = (y_sum - slope * x_sum) / float(n)
        
        projection = [intercept + slope * (n + i) for i in range(periods)]
        return Ok(projection)

    def diagnostics(self) -> dict:
        """Return engine diagnostic metadata.

        Returns:
            dict: Engine name, version, and operational status.
        """
        return {"engine": "OmniTimeSeriesForecastingEngine", "version": "1.0.0", "status": "operational"}
