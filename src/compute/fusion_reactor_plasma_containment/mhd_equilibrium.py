import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class MhdEquilibrium:
    def __init__(self):
        pass

    def compute_magnetic_pressure(self, magnetic_field_tesla: float, plasma_pressure_pa: float) -> OmniResult:
        if magnetic_field_tesla < 0 or plasma_pressure_pa < 0:
            return OmniResult(error="Parameters must be non-negative")

        # Deterministic calculation of Magnetohydrodynamic (MHD) Equilibrium
        # In a Tokamak Fusion Reactor, the outward pressure of the 100-million-degree plasma
        # must be perfectly balanced by the inward pressure of the confining magnetic fields.
        try:
            # Magnetic pressure P_mag = B^2 / (2 * mu_0)
            mu_0 = 4 * math.pi * 1e-7 # Vacuum permeability
            p_mag = (magnetic_field_tesla ** 2) / (2 * mu_0)
            
            # Beta = Plasma Pressure / Magnetic Pressure
            # Beta must remain below the Troyon limit to avoid catastrophic disruption
            plasma_beta = plasma_pressure_pa / p_mag
            
            return OmniResult(value={"magnetic_pressure_pa": p_mag, "plasma_beta": plasma_beta})
        except Exception as e:
            return OmniResult(error=str(e))
