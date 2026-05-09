<?php

namespace Omni\Business\Camera;

/**
 * 🪐 OMNI MOTHER DEEP THINKING & ARCHITECTURAL BLUEPRINT 🪐
 * LAYER: Business Layer | DOMAIN: Camera Frame Rate Analyzer | LANG: PHP
 */
class FrameAnalyzer {
    private float $startTime;
    private int $frameCount = 0;

    public function __construct() {
        $this->startTime = microtime(true);
    }

    /**
     * Analyze a new frame and calculate FPS.
     */
    public function recordFrame(): void {
        $this->frameCount++;
    }

    /**
     * Get the current FPS.
     * @return float
     */
    public function getFps(): float {
        $duration = microtime(true) - $this->startTime;
        if ($duration <= 0) return 0.0;
        return $this->frameCount / $duration;
    }

    /**
     * Reset the analyzer.
     */
    public function reset(): void {
        $this->startTime = microtime(true);
        $this->frameCount = 0;
    }
}

// Local testing
if (php_sapi_name() === 'cli') {
    $analyzer = new FrameAnalyzer();
    for ($i = 0; $i < 60; $i++) {
        $analyzer->recordFrame();
        usleep(16666); // Simulating ~60fps
    }
    echo "🎥 Current FPS Analysis: " . round($analyzer->getFps(), 2) . "\n";
}