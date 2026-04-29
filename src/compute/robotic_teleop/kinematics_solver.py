import ctypes
import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class KinematicsSolver:
    def __init__(self):
        self.lib = ctypes.CDLL('./system/robotic_teleop/servo_controller_ffi.so')
        self.lib.omni_calculate_ik.argtypes = [ctypes.c_double, ctypes.c_double, ctypes.c_double, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_int)]
        self.lib.omni_calculate_ik.restype = None

    def solve_inverse_kinematics(self, x: float, y: float, z: float) -> OmniResult:
        # Basic validation
        distance = math.sqrt(x*x + y*y + z*z)
        if distance > 1.5:  # Max reach of 1.5m
            return OmniResult(error="Target out of reach")

        err_code = ctypes.c_int(0)
        joint_angles = (ctypes.c_double * 6)() # 6 DOF arm
        
        self.lib.omni_calculate_ik(x, y, z, joint_angles, ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"IK Solver failed with code {err_code.value}")

        return OmniResult(value={
            'target': {'x': x, 'y': y, 'z': z},
            'joints': list(joint_angles)
        })
