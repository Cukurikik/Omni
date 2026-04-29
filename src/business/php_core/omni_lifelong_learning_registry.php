<?php
// Omni Lifelong Learning Registry (PHP)
// Business Layer: Registration and tracking of continual learning experiments.
// Ref: zzz47zzz/awesome-lifelong-learning-methods-for-llm

declare(strict_types=1);

final class LifelongExperiment {
    public readonly string $name;
    public readonly string $method;
    public readonly float $forgettingRate;
    public readonly float $accuracy;

    public function __construct(string $name, string $method, float $forgettingRate, float $accuracy) {
        $this->name = $name;
        $this->method = $method;
        $this->forgettingRate = max(0.0, min(1.0, $forgettingRate));
        $this->accuracy = max(0.0, min(1.0, $accuracy));
    }
}

final class OmniLifelongRegistry {
    /** @var LifelongExperiment[] */
    private array $experiments = [];

    public function register(LifelongExperiment $exp): void {
        $this->experiments[] = $exp;
    }

    public function getBestByAccuracy(): ?LifelongExperiment {
        if (empty($this->experiments)) return null;
        $best = $this->experiments[0];
        foreach ($this->experiments as $exp) {
            if ($exp->accuracy > $best->accuracy) $best = $exp;
        }
        return $best;
    }

    public function averageForgetting(): float {
        if (empty($this->experiments)) return 0.0;
        $sum = array_sum(array_map(fn($e) => $e->forgettingRate, $this->experiments));
        return round($sum / count($this->experiments), 6);
    }
}
