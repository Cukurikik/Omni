<?php

namespace Omni\Domain\BioSignal;

// OMNI BIO-SIGNAL CLASSIFIER DOMAIN
// Physiological thresholds mapping validation structures.

class BioSignalResult {
    public float $value;
    public string $error;
    public bool $is_ok;

    public function __construct(float $v, string $e, bool $ok) {
        $this->value = $v;
        $this->error = $e;
        $this->is_ok = $ok;
    }
}

class BioSignalValidator {
    private float $max_heart_rate_bpm;
    private float $min_oxygen_saturation;

    public function __construct(float $max_hr = 220.0, float $min_o2 = 85.0) {
        $this->max_heart_rate_bpm = $max_hr;
        $this->min_oxygen_saturation = $min_o2;
    }

    public function validate_physiological_state(float $heart_rate, float $oxygen_sat): BioSignalResult {
        if ($heart_rate <= 0.0 || $oxygen_sat <= 0.0) {
            return new BioSignalResult(0.0, "INVALID_ZERO_OR_NEGATIVE_SIGNAL", false);
        }

        if ($heart_rate > $this->max_heart_rate_bpm) {
            return new BioSignalResult(0.0, "HEART_RATE_EXCEEDED_DOMAIN_LIMIT", false);
        }

        if ($oxygen_sat < $this->min_oxygen_saturation) {
            return new BioSignalResult(0.0, "OXYGEN_SATURATION_CRITICAL_BOUND", false);
        }

        // Domain index metric proxy
        $stress_index = ($heart_rate / $this->max_heart_rate_bpm) + (1.0 - ($oxygen_sat / 100.0));
        
        return new BioSignalResult($stress_index, "", true);
    }
}
