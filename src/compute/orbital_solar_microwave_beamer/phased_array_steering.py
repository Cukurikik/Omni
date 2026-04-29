import math

class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class PhasedArraySteering:
    def __init__(self):
        pass

    def compute_phase_shift(self, antenna_element_index: int, element_spacing_meters: float, target_angle_rad: float, frequency_hz: float) -> OmniResult:
        if element_spacing_meters <= 0 or frequency_hz <= 0:
            return OmniResult(error="Spacing and frequency must be positive")

        # Deterministic calculation of Phased Array Microwave Beam Steering.
        # An orbital solar power satellite collects 1 Gigawatt of solar energy.
        # Instead of physically moving a massive dish, it electronically steers a microwave beam
        # down to Earth by slightly delaying (phase shifting) the signal emitted from thousands of tiny antennas.
        try:
            # Wavelength lambda = c / f
            c_light = 299792458.0
            wavelength = c_light / frequency_hz
            
            # Phase shift formula: DeltaPhi = (2 * pi / lambda) * d * sin(theta) * index
            # This calculates the exact electrical delay needed for a specific antenna element
            # to constructively interfere at the target angle.
            
            k = (2.0 * math.pi) / wavelength
            phase_shift_rad = k * element_spacing_meters * math.sin(target_angle_rad) * antenna_element_index
            
            # Normalize to [-pi, pi]
            normalized_phase = (phase_shift_rad + math.pi) % (2.0 * math.pi) - math.pi
            
            return OmniResult(value=normalized_phase)
        except Exception as e:
            return OmniResult(error=str(e))
