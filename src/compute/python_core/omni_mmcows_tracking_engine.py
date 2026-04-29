import uuid
from typing import Dict, Any, Tuple
from dataclasses import dataclass, field
import numpy as np

# OMNI Monadic Type
@dataclass
class Result:
    is_ok: bool
    value: Any = None
    error: str = None

    @classmethod
    def Ok(cls, value: Any):
        return cls(is_ok=True, value=value)

    @classmethod
    def Err(cls, error: str):
        return cls(is_ok=False, error=error)

def ok(value: Any) -> Result:
    return Result.Ok(value)

def err(error: str) -> Result:
    return Result.Err(error)

@dataclass
class OmniMmcowsTrackingEngine:
    """
    OmniMmcowsTrackingEngine
    Domain: MmCows (Multimodal Dataset for Dairy Cattle Monitoring)
    Calculates multimodal data fusion utilizing a standard Extended Kalman Filter (EKF) step.
    It non-linearly aggregates Ultra-Wideband (UWB) distance and Visual bounding box arrays.
    """
    engine_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    dt: float = 0.1 # Time step

    def _ekf_fusion(self, x: np.ndarray, P: np.ndarray, uwb_z: float, visual_pos: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extened Kalman Filter state array updates
        x = [pos_x, pos_y, vel_x, vel_y]^T
        """
        # State transition matrix F
        F = np.array([
            [1, 0, self.dt, 0],
            [0, 1, 0, self.dt],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=np.float32)

        # Process noise covariance Q
        q_sigma = 0.05
        Q = np.eye(4) * q_sigma

        # 1. Predict
        x_pred = F @ x
        P_pred = F @ P @ F.T + Q

        # Multimodal Measurement Update
        # Visual Measurement (linear mapping [x, y])
        H_vis = np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0]
        ], dtype=np.float32)
        R_vis = np.eye(2) * 0.1  # Variance in visual detection

        # Calculate visual kalman gain
        S_vis = H_vis @ P_pred @ H_vis.T + R_vis
        K_vis = P_pred @ H_vis.T @ np.linalg.inv(S_vis)

        # Visual update step
        y_vis = visual_pos - (H_vis @ x_pred)
        x_upd1 = x_pred + K_vis @ y_vis
        P_upd1 = (np.eye(4) - K_vis @ H_vis) @ P_pred

        # UWB Measurement (non-linear distance mapping from origin (0,0))
        # h(x) = sqrt(x[0]^2 + x[1]^2)
        dist = np.sqrt(x_upd1[0]**2 + x_upd1[1]**2) + 1e-8
        
        # Jacobian H_uwb
        H_uwb = np.array([
            [x_upd1[0]/dist, x_upd1[1]/dist, 0.0, 0.0]
        ], dtype=np.float32)
        R_uwb = np.array([[0.5]]) # Variance in UWB (usually higher noise but absolute)

        # Calculate UWB kalman gain
        S_uwb = H_uwb @ P_upd1 @ H_uwb.T + R_uwb
        K_uwb = P_upd1 @ H_uwb.T @ np.linalg.inv(S_uwb)

        # UWB Update Step
        y_uwb = uwb_z - dist
        x_upd2 = x_upd1 + (K_uwb @ np.array([y_uwb])).reshape(-1)
        
        P_upd2 = (np.eye(4) - K_uwb @ H_uwb) @ P_upd1

        return x_upd2, P_upd2

    def process(self, payload: Dict[str, Any]) -> Result:
        try:
            if "state" not in payload or "covariance" not in payload:
                return err("Initial state or covariance missing")
            if "uwb_distance" not in payload or "visual_position" not in payload:
                return err("Multimodal measurements (uwb_distance, visual_position) missing")

            x = np.array(payload["state"], dtype=np.float32)
            P = np.array(payload["covariance"], dtype=np.float32)
            uwb_z = float(payload["uwb_distance"])
            visual_pos = np.array(payload["visual_position"], dtype=np.float32)

            if x.shape != (4,) or P.shape != (4, 4) or visual_pos.shape != (2,):
                return err("Invalid dimension in state variables. Expected x:(4,), P:(4,4), visual_pos:(2,)")

            # Execute EKF fusion
            x_fused, P_fused = self._ekf_fusion(x, P, uwb_z, visual_pos)

            return ok({
                "engine_id": self.engine_id,
                "fused_state": x_fused.tolist(),
                "fused_covariance": P_fused.tolist(),
                "status": "MmCows Tracker Update Complete"
            })
        except Exception as e:
            return err(f"Mmcows Tracking failed: {str(e)}")

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniMmcowsTrackingEngine",
            "status": "Operational",
            "dt": self.dt
        }
