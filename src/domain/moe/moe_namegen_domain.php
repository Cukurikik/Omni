<?php
// moe_namegen_domain.php — Domain Layer: Name Generator Content Filter
// PHP domain logic applying strict profanity and quality filters to generated AI names.

namespace Omni\Domain\MoE\NameGen;

class ContentFilter {
    private array $bannedWords = ['spam', 'test', 'admin', 'root'];

    public function isNameAcceptable(string $generatedName): bool {
        $nameLower = strtolower(trim($generatedName));

        // Enforce length constraints (Seq2Seq models can hallucinate endlessly)
        if (strlen($nameLower) < 3 || strlen($nameLower) > 25) {
            return false;
        }

        // Check against banlist
        foreach ($this->bannedWords as $banned) {
            if (strpos($nameLower, $banned) !== false) {
                return false;
            }
        }

        // Must contain only letters, numbers, and basic punctuation
        if (!preg_match('/^[a-zA-Z0-9\-\_]+$/', $nameLower)) {
            return false;
        }

        return true;
    }
}
?>
