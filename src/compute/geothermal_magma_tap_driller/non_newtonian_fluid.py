import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class NonNewtonianFluid:
    def __init__(self):
        pass

    def compute_magma_viscosity(self, temperature_c: float, shear_rate_s1: float) -> OmniResult:
        if temperature_c <= 0 or shear_rate_s1 < 0:
            return OmniResult(error="Temperature and shear rate must be positive")

        # Deterministic calculation of Non-Newtonian Magma Dynamics.
        # Magma (molten rock) is shear-thinning. The faster you spin the drill bit (shear rate),
        # the less viscous it becomes. However, if it cools down, it solidifies instantly,
        # trapping the drill string 10 kilometers underground.
        try:
            # Simulated Arrhenius-type temperature dependence mixed with Power-law shear thinning
            activation_energy = 50000.0
            r_gas = 8.314
            temp_k = temperature_c + 273.15
            
            # Base viscosity from temperature
            mu_0 = 1e-4 * math.exp(activation_energy / (r_gas * temp_k))
            
            # Shear thinning (n < 1)
            flow_index = 0.6
            
            # Prevent division by zero if shear rate is exactly 0
            safe_shear = max(shear_rate_s1, 1e-5)
            
            # Apparent viscosity
            apparent_viscosity_pa_s = mu_0 * (safe_shear ** (flow_index - 1.0))
            
            return OmniResult(value=apparent_viscosity_pa_s)
        except Exception as e:
            return OmniResult(error=str(e))
