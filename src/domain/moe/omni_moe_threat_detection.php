<?php

namespace Omni\Domain\MoE;

/**
 * OMNI MOTHER Production Zero-Mock Threat Detection
 * Real-time analysis of prompt injection, prompt leaking, and jailbreak attempts
 * prior to passing context to the underlying MoE Router.
 */
class PromptThreatDetector {
    
    // Core systemic directives that must not be overridden
    private const CRITICAL_HEURISTICS = [
        'ignore previous instructions',
        'you are a developer mode',
        'system prompt bypass',
        'reveal your system prompt',
        'forget all previous commands',
        'print instructions above'
    ];

    /**
     * @param string $input User prompt
     * @return array Result monadic structure
     */
    public function analyzePrompt(string $input): array {
        
        $normalized = strtolower(trim($input));
        $riskScore = 0.0;
        $matchedPatterns = [];

        // 1. Heuristic Scan
        foreach (self::CRITICAL_HEURISTICS as $heuristic) {
            if (strpos($normalized, $heuristic) !== false) {
                $riskScore += 0.8; // High weight for explicit jailbreaks
                $matchedPatterns[] = $heuristic;
            }
        }

        // 2. Entropy Scan (Detects obfuscated/encoded injections like Base64/Hex)
        $entropy = $this->calculateShannonEntropy($input);
        if ($entropy > 4.5 && strlen($input) > 20) {
            $riskScore += 0.3;
            $matchedPatterns[] = 'high_entropy_obfuscation';
        }

        // 3. Evaluation
        if ($riskScore >= 0.8) {
            return [
                'is_safe' => false,
                'risk_score' => $riskScore,
                'action' => 'BLOCK',
                'reason' => 'OMNI CRITICAL: Jailbreak or Prompt Injection Detected',
                'matches' => $matchedPatterns
            ];
        }

        return [
            'is_safe' => true,
            'risk_score' => $riskScore,
            'action' => 'ALLOW',
            'reason' => 'Clear'
        ];
    }

    private function calculateShannonEntropy(string $str): float {
        $len = strlen($str);
        if ($len === 0) return 0.0;
        
        $frequencies = array_count_values(str_split($str));
        $entropy = 0.0;
        
        foreach ($frequencies as $freq) {
            $p = $freq / $len;
            $entropy -= $p * log($p, 2);
        }
        
        return $entropy;
    }
}
