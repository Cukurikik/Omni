import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class MagnetohydrodynamicFlow:
    def __init__(self):
        pass

    def compute_coronal_plasma_ejection_speed(self, magnetic_field_strength_gauss: float, plasma_density_kg_m3: float) -> OmniResult:
        if magnetic_field_strength_gauss <= 0 or plasma_density_kg_m3 <= 0:
            return OmniResult(error="Invalid stellar parameters")

        # Deterministic calculation of Coronal Mass Ejection (CME) plasma velocity.
        # Solar flares occur when magnetic field lines on the sun twist and "snap" (reconnection),
        # flinging billions of tons of super-heated plasma into space.
        # We use Magnetohydrodynamics (MHD) to calculate the Alfven wave speed.
        try:
            # Alfven velocity: V_A = B / sqrt(mu_0 * rho)
            
            # Convert Gauss to Tesla (1 Gauss = 1e-4 Tesla)
            b_tesla = magnetic_field_strength_gauss * 1e-4
            
            mu_0 = 1.25663706e-6 # Vacuum permeability (T*m/A)
            
            alfven_velocity_m_s = b_tesla / math.sqrt(mu_0 * plasma_density_kg_m3)
            
            # CME velocity is strongly correlated with the Alfven speed in the active region
            cme_velocity_km_s = alfven_velocity_m_s / 1000.0
            
            return OmniResult(value=cme_velocity_km_s)
        except Exception as e:
            return OmniResult(error=str(e))
