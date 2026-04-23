import datetime
from typing import Any, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class OmniPIDControllerFeedbackEngine:
    """
    OmniPIDControllerFeedbackEngine
    Batch: 29 (Semester 10)
    
    A zero-mock systems automation engine executing Proportional-Integral-Derivative 
    mathematical adjustments calculating closed-loop temporal frame shifts.
    """
    
    def __init__(self, kp: float, ki: float, kd: float, setpoint: float):
        """
        :param kp: Proportional gain
        :param ki: Integral gain
        :param kd: Derivative gain
        :param setpoint: The mathematical absolute target boundary limit
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.setpoint = setpoint
        
        self.integral = 0.0
        self.previous_error = 0.0

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.__class__.__name__,
            "status": "operational",
            "kp": self.kp,
            "ki": self.ki,
            "kd": self.kd,
            "setpoint": self.setpoint,
            "integral_accumulation": round(self.integral, 4),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

    def compute_correction(self, process_variable: float, dt_seconds: float) -> Result[Dict[str, float], Exception]:
        """
        Advances the PID logical cycle and produces an absolute numerical offset correction command.
        """
        try:
            if dt_seconds <= 0:
                return Err(ValueError("Delta time (dt) must be strictly positive"))
                
            error = self.setpoint - process_variable
            
            # Proportional
            p_out = self.kp * error
            
            # Integral with anti-windup abstract clamp limits to execute hardware bounds
            self.integral += error * dt_seconds
            # Hard limit accumulator strictly for sanity
            self.integral = max(-1000.0, min(self.integral, 1000.0))
            i_out = self.ki * self.integral
            
            # Derivative
            derivative = (error - self.previous_error) / dt_seconds
            d_out = self.kd * derivative
            
            # Record state
            self.previous_error = error
            
            output = p_out + i_out + d_out
            
            return Ok({
                "process_variable": process_variable,
                "error": round(error, 4),
                "p_out": round(p_out, 4),
                "i_out": round(i_out, 4),
                "d_out": round(d_out, 4),
                "correction": round(output, 4)
            })
            
        except Exception as e:
            return Err(e)

    def reset_state(self) -> Result[bool, Exception]:
        """
        Wipes integral accumulation and previous error states back to zero.
        """
        try:
            self.integral = 0.0
            self.previous_error = 0.0
            return Ok(True)
        except Exception as e:
            return Err(e)
