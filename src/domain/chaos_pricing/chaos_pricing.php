<?php

namespace Omni\Semester13\Batch08;

class ChaosPricingError extends \Exception {}

class Result {
    public $value;
    public $error;

    public function __construct($value = null, $error = null) {
        $this->value = value;
        $this->error = error;
    }

    public function isOk() {
        return $this->error === null;
    }

    public function unwrap() {
        if (!$this->isOk()) {
            throw $this->error;
        }
        return $this->value;
    }
}

/**
 * OMNI Engine: chaos-financials
 * Dynamic pricing mapping based on algorithmic entropy density (Chaos scaling).
 */
class ChaosPricingEngine {
    private $baseMultiplier;

    public function __construct($baseMultiplier = 2.5) {
        $this->baseMultiplier = $baseMultiplier;
    }

    public function calculate_entropy_premium($lyapunov_exponent) {
        try {
            if ($lyapunov_exponent < -10.0 || $lyapunov_exponent > 10.0) {
                return new Result(null, new ChaosPricingError("Lyapunov exponent topologically outside pricing scope"));
            }

            // High chaos (positive exponent) = higher compute premium
            $modifier = 1.0;
            if ($lyapunov_exponent > 0.0) {
                $modifier = 1.0 + ($lyapunov_exponent * 0.5);
            }

            $total_premium = $this->baseMultiplier * $modifier;

            return new Result([
                'pricing_premium' => $total_premium,
                'is_chaotic_compute' => $lyapunov_exponent > 0.0
            ]);
        } catch (\Exception $e) {
            return new Result(null, new ChaosPricingError("Premium matrix failed: " . $e->getMessage()));
        }
    }
}
