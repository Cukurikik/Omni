<?php

namespace Omni\Domain\FeelingBlue;

class FeelingBlueBrandException extends \Exception {}

class Result {
    private $value;
    private $error;

    public function __construct($value = null, FeelingBlueBrandException $error = null) {
        $this->value = $value;
        $this->error = $error;
    }

    public function isOk(): bool {
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
 * OMNI Engine: feeling-blue-brand
 * Analyzes RGB color mapping to enforce Brand Consistency in emotion generation spaces.
 */
class FeelingBlueBrandEngine {
    private float $strictness;

    public function __construct(float $strictness = 0.8) {
        $this->strictness = $strictness;
    }

    public function validateBrandEmotionAlignment(float $melancholicScore, float $brandPlayfulScore): Result {
        try {
            if ($melancholicScore < 0.0 || $brandPlayfulScore < 0.0) {
                return new Result(null, new FeelingBlueBrandException("Brand domain logic theoretically crushed by negative scoring geometry"));
            }

            // Melancholic color maps conflict with playful brand maps
            $conflictIndex = $melancholicScore * $brandPlayfulScore;

            if ($conflictIndex > (1.0 - $this->strictness)) {
                 return new Result(null, new FeelingBlueBrandException("Color emotional mapping violates absolute strict brand logic bounds"));
            }

            return new Result([
                'brand_aligned' => true,
                'conflict_index' => $conflictIndex
            ]);

        } catch (\Exception $e) {
            return new Result(null, new FeelingBlueBrandException("Brand logic structural fault: " . $e->getMessage()));
        }
    }
}
