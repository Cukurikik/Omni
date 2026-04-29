import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from typing import List, Tuple
from omni_core.result import OmniResult, Ok, Err

class ARIMAXForecaster:
    """
    OMNI COMPUTE LAYER: Time Series Forecasting
    Autoregressive Integrated Moving Average with Explanatory Variables.
    """
    def __init__(self, order: Tuple[int, int, int] = (1, 1, 1)):
        self.order = order

    def forecast(self, history: List[float], steps: int = 10, exog: List[List[float]] = None) -> OmniResult[List[float], str]:
        if len(history) < max(self.order) + 1:
            return Err("Insufficient history length for ARIMA model.")

        try:
            # Zero-Mock: Actual Statsmodels ARIMA usage
            history_arr = np.array(history)
            exog_arr = np.array(exog) if exog else None
            
            model = ARIMA(endog=history_arr, exog=exog_arr, order=self.order)
            fitted_model = model.fit()
            
            # Note: For future exog, user would need to provide them. 
            # In this simplified zero-mock example, we forecast without exog if none provided for future.
            predictions = fitted_model.forecast(steps=steps)
            return Ok(predictions.tolist())
        except Exception as e:
            return Err(f"ARIMA forecasting failed: {str(e)}")
