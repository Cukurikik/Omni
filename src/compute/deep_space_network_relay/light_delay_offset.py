class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class LightDelayOffset:
    def __init__(self):
        pass

    def compute_one_way_light_time(self, distance_km: float) -> OmniResult:
        if distance_km < 0:
            return OmniResult(error="Distance cannot be negative")

        # Deterministic calculation of One-Way Light Time (OWLT)
        # Deep space communication (e.g., Earth to Mars) is not instantaneous.
        # We must calculate exactly how long a radio signal takes to reach the rover
        # to properly sequence and timestamp commands via the Deep Space Network (DSN).
        try:
            # Speed of light in vacuum (km/s)
            c_km_s = 299792.458
            
            owlt_seconds = distance_km / c_km_s
            
            return OmniResult(value=owlt_seconds)
        except Exception as e:
            return OmniResult(error=str(e))
