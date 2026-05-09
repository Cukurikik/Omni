<?php

namespace Omni\Domain\MoE;

/**
 * OMNI MOTHER Production Zero-Mock GDPR Masking
 * Pre-processes prompts before hitting MoE to mask European PII formats,
 * ensuring compliance with strict data protection regimes.
 */
class GdprDataMasker {
    
    // Regex maps tailored for European data
    private const EU_PATTERNS = [
        'UK_NINO' => '/\b[A-CEGHJ-PR-TW-Z]{1}[A-CEGHJ-NPR-TW-Z]{1}[0-9]{6}[A-D\s]{1}\b/i',
        'IBAN' => '/\b[A-Z]{2}[0-9]{2}(?:[ ]?[0-9a-zA-Z]{4}){3,7}\b/',
        'PHONE_EU' => '/(?:\+?(?:44|49|33|34|39|41)\s?|0)(?:\d\s?){9,10}\b/',
        'EMAIL' => '/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/'
    ];

    public function anonymizePrompt(string $prompt, string $tenantId): array {
        $maskedPrompt = $prompt;
        $replacements = [];
        $counter = 1;

        foreach (self::EU_PATTERNS as $type => $pattern) {
            $maskedPrompt = preg_replace_callback($pattern, function($matches) use (&$replacements, &$counter, $type) {
                $token = "[REDACTED_{$type}_{$counter}]";
                $replacements[$token] = $matches[0];
                $counter++;
                return $token;
            }, $maskedPrompt);
        }

        // Return the masked prompt for inference, and the vault map to unmask later if needed
        return [
            'safe_prompt' => $maskedPrompt,
            'vault_map' => $replacements,
            'tenant' => $tenantId
        ];
    }

    public function rehydrateResponse(string $llmResponse, array $vaultMap): string {
        $hydrated = $llmResponse;
        foreach ($vaultMap as $token => $originalValue) {
            // Note: LLM might slightly alter the token whitespace, 
            // a robust system uses rigid delimiters.
            $hydrated = str_replace($token, $originalValue, $hydrated);
        }
        return $hydrated;
    }
}
