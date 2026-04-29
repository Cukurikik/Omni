import ctypes
import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class FaceLandmarkMath:
    def __init__(self):
        self.lib = ctypes.CDLL('./system/anime_animator/morph_target_ffi.so')
        self.lib.omni_apply_affine_transform.argtypes = [
            ctypes.POINTER(ctypes.c_double), # current points
            ctypes.c_int,                    # num points
            ctypes.c_double,                 # scale
            ctypes.c_double,                 # rotation
            ctypes.c_double,                 # tx
            ctypes.c_double,                 # ty
            ctypes.POINTER(ctypes.c_double), # output points
            ctypes.POINTER(ctypes.c_int)     # error code
        ]
        self.lib.omni_apply_affine_transform.restype = None

    def calculate_transformation(self, base_landmarks: list[float], pitch: float, yaw: float, roll: float) -> OmniResult:
        if not base_landmarks or len(base_landmarks) % 2 != 0:
            return OmniResult(error="Invalid landmark coordinate array length")

        num_pts = len(base_landmarks) // 2
        input_arr = (ctypes.c_double * len(base_landmarks))(*base_landmarks)
        output_arr = (ctypes.c_double * len(base_landmarks))()
        err_code = ctypes.c_int(0)

        # Deterministic math for 2D projection of 3D Euler angles
        # Scale decreases as pitch/yaw pushes face away
        scale_factor = math.cos(pitch) * math.cos(yaw)
        
        # Translation maps directly to yaw/pitch in a 2D plane
        tx = math.sin(yaw) * 50.0 
        ty = math.sin(pitch) * 50.0

        # System FFI offload for matrix multiplication across all vertices
        self.lib.omni_apply_affine_transform(
            input_arr, 
            num_pts, 
            scale_factor, 
            roll, 
            tx, 
            ty, 
            output_arr, 
            ctypes.byref(err_code)
        )

        if err_code.value != 0:
            return OmniResult(error=f"Affine transform FFI failed: {err_code.value}")

        return OmniResult(value=list(output_arr))
