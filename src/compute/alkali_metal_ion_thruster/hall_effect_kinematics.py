import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class HallEffectKinematics:
    def __init__(self):
        pass

    def compute_plasma_exhaust_velocity(self, grid_voltage: float, ion_mass_kg: float) -> OmniResult:
        if grid_voltage <= 0 or ion_mass_kg <= 0:
            return OmniResult(error="Invalid thruster parameters")

        # Deterministic calculation of Hall-Effect Ion Thruster Kinematics.
        # Ion drives don't burn chemical fuel. They use electricity to strip electrons
        # from a heavy gas (like Xenon), then use strong electrostatic grids to accelerate
        # the ions out the back at extreme velocities (up to 50 km/s).
        try:
            # Physics: Kinetic Energy = Electrical Potential Energy
            # 1/2 * m * v^2 = q * V
            
            elementary_charge = 1.60217663e-19 # Coulombs
            
            # Solve for v (exhaust velocity)
            # v = sqrt((2 * q * V) / m)
            
            numerator = 2.0 * elementary_charge * grid_voltage
            exhaust_velocity_m_s = math.sqrt(numerator / ion_mass_kg)
            
            return OmniResult(value=exhaust_velocity_m_s)
        except Exception as e:
            return OmniResult(error=str(e))
