import math

class ECGLanguageError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self):
        if not self.is_ok():
            raise self.error
        return self.value

# OMNI Engine: ecg-language
# Maps physiological signals (ECG waves) to language token bounds.
class ECGLanguageEngine:
    def __init__(self, default_hz: float = 250.0):
        self.hz = default_hz

    def evaluate_signal_tokenization(self, duration_seconds: float, detected_qrs_complexes: int) -> Result:
        try:
            if duration_seconds <= 0.0 or detected_qrs_complexes < 0:
                return Result(error=ECGLanguageError("ECG temporal matrices inverted or null"))

            # Calculate BPM from the signal mapping
            bpm = (detected_qrs_complexes / duration_seconds) * 60.0

            if bpm > 300.0 or bpm < 20.0:
                # Physiologically impossible or lethal state; reject language mapping as hallucinated noise
                return Result(value={"valid_signal": False, "bpm": bpm, "token_density": 0.0})

            # Token density is higher when heartbeat is elevated
            token_density = math.log10(bpm) * 1.5

            return Result(value={
                "valid_signal": True,
                "bpm": bpm,
                "token_density": token_density
            })

        except Exception as e:
            return Result(error=ECGLanguageError(f"ECG semantics translation fault: {str(e)}"))
