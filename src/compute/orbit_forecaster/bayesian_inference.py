import ctypes
import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class BayesianInference:
    def __init__(self, num_samples: int = 1000):
        self.num_samples = num_samples
        self.lib = ctypes.CDLL('./system/orbit_forecaster/mcmc_sampler_ffi.so')
        self.lib.omni_mcmc_sample.argtypes = [
            ctypes.POINTER(ctypes.c_double), 
            ctypes.c_int, 
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_int)
        ]
        self.lib.omni_mcmc_sample.restype = None

    def calculate_posterior(self, prior_data: list[float]) -> OmniResult:
        if not prior_data:
            return OmniResult(error="Prior data cannot be empty")

        data_len = len(prior_data)
        input_arr = (ctypes.c_double * data_len)(*prior_data)
        output_arr = (ctypes.c_double * self.num_samples)()
        err_code = ctypes.c_int(0)

        # Offload heavy MCMC sampling to system FFI
        self.lib.omni_mcmc_sample(input_arr, data_len, self.num_samples, output_arr, ctypes.byref(err_code))

        if err_code.value != 0:
            return OmniResult(error=f"MCMC sampling failed with code {err_code.value}")

        # Deterministic statistics on posterior
        posterior = list(output_arr)
        mean_val = sum(posterior) / self.num_samples
        variance = sum((x - mean_val) ** 2 for x in posterior) / self.num_samples
        
        return OmniResult(value={
            "posterior_samples": posterior,
            "mean": mean_val,
            "variance": variance,
            "std_dev": math.sqrt(variance)
        })
