import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class QuadrupolePotential:
    def __init__(self):
        pass

    def compute_trap_frequency(self, particle_charge_coulombs: float, particle_mass_kg: float, magnetic_field_tesla: float) -> OmniResult:
        if particle_mass_kg <= 0 or magnetic_field_tesla <= 0:
            return OmniResult(error="Mass and magnetic field must be positive")

        # Deterministic calculation of Penning Trap frequencies for Antimatter containment.
        # Antimatter (like positrons or antiprotons) will annihilate instantly if it touches normal matter.
        # We suspend it in a perfect vacuum using a strong, uniform axial magnetic field
        # and a quadrupole electric field (a Penning trap).
        try:
            # Cyclotron frequency (omega_c = qB / m)
            # The frequency at which the antimatter particle orbits the magnetic field lines.
            omega_c = (abs(particle_charge_coulombs) * magnetic_field_tesla) / particle_mass_kg
            
            return OmniResult(value=omega_c)
        except Exception as e:
            return OmniResult(error=str(e))
