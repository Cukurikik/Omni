// OMNI HAPTIC FEEDBACK UI
// Flutter Widget-to-native API calls validation layer limits.

class OmniHapticResult {
  final bool isOk;
  final String error;
  final bool canVibrate;

  OmniHapticResult(this.isOk, this.error, this.canVibrate);
}

class OmniHapticFeedbackEngine {
  final int maxIntensity;
  final int maxDurationMs;

  OmniHapticFeedbackEngine({required this.maxIntensity, required this.maxDurationMs});

  OmniHapticResult validateHapticRequest(int intensity, int durationMs, bool permissionGranted) {
    if (!permissionGranted) {
      return OmniHapticResult(false, "HAPTIC_PERMISSION_DENIED", false);
    }

    if (intensity < 0 || durationMs < 0) {
      return OmniHapticResult(false, "NEGATIVE_HAPTIC_PARAMETERS", false);
    }

    if (intensity > maxIntensity) {
       return OmniHapticResult(false, "INTENSITY_LIMIT_EXCEEDED", false);
    }

    if (durationMs > maxDurationMs) {
       return OmniHapticResult(false, "DURATION_LIMIT_EXCEEDED", false);
    }

    // Zero-mock bounds return representing safe proxy dispatch
    return OmniHapticResult(true, "", true);
  }
}
