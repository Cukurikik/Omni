from omni.core import Result, Ok, Err

class TSForecaster:
    def forecast(self, timeseries: list[float], horizon: int) -> Result[list[float], ValueError]:
        if not timeseries or horizon <= 0:
            return Err(ValueError("Invalid timeseries or horizon"))
        return Ok([timeseries[-1]] * horizon)
