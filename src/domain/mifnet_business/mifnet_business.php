<?php

namespace Omni\Domain\MifnetBusiness;

// OMNI Engine: MifNet Business
// PHP Domain Layer enforcing enterprise-grade usage restrictions for fusion geometry matrices.

class MifnetDomainError extends \Exception {}

class Result {
    private $value;
    private $error;

    private function __construct($value, ?MifnetDomainError $error) {
        $this->value = $value;
        $this->error = $error;
    }

    public static function ok($value): self {
        return new self($value, null);
    }

    public static function err(string $msg): self {
        return new self(null, new MifnetDomainError($msg));
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

class FusionResourcePolicy {
    private float $maxMegapixels;

    public function __construct(float $maxMegapixels = 50.0) {
        $this->maxMegapixels = $maxMegapixels;
    }

    public function authorizeFusionRequest(int $width, int $height, string $licenseType): Result {
        if ($width <= 0 || $height <= 0) {
            return Result::err("Mathematical bounds failure: Image dimensions must be strictly positive geometries.");
        }

        $megapixels = ($width * $height) / 1000000.0;
        
        if ($licenseType !== "ENTERPRISE" && $megapixels > $this->maxMegapixels) {
            return Result::err(sprintf(
                "Usage violation: Pixel geometry %.2f MP exceeds standard license constraint %.2f MP", 
                $megapixels, 
                $this->maxMegapixels
            ));
        }

        return Result::ok(true);
    }
    
    public function calculateEntropyTax(float $informationEntropy): Result {
         if ($informationEntropy < 0.0) {
             return Result::err("Thermodynamic constraint error: Entropy cannot be negative.");
         }
         
         // Mathematical tax scaling
         $tax = log10($informationEntropy + 1.0) * 0.05;
         return Result::ok($tax);
    }
}
