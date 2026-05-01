// OMNI MOTHER SYSTEM - SECURITY LAYER
// LLM Prompt Injection Filter
// Detects and neutralizes semantic adversarial payloads in scalable chatbots.

export type OmniResult<T, E> = 
  | { success: true; value: T; error: null }
  | { success: false; value: null; error: E };

export class PromptInjectionFilter {
    // High-entropy regex patterns of known jailbreaks (e.g., DAN, Ignore Previous Instructions)
    private readonly adversarialPatterns = [
        /ignore\s+(all\s+)?previous\s+(instructions|prompts|directions)/i,
        /disregard\s+(all\s+)?previous/i,
        /system\s+override/i,
        /you\s+are\s+now\s+in\s+(developer|unrestricted|god)\s+mode/i,
        /bypass\s+filters/i,
        /comput\s+an\s+ai\s+that\s+does\s+not/i,
        /<\|system\|>/i // Appending special tokens manually
    ];

    /**
     * @brief Defends the Chatbot API from injection strings.
     * Evaluates prompt logic and strips adversarial command attempts.
     */
    public sanitizeUserPrompt(rawInput: string): OmniResult<string, string> {
        if (!rawInput || rawInput.trim() === '') {
            return { success: false, value: null, error: "Empty prompt provided." };
        }

        let sanitized = rawInput;

        // 1. Check for immediate system overrides
        for (const pattern of this.adversarialPatterns) {
            if (pattern.test(sanitized)) {
                return { success: false, value: null, error: "OMNI_FATAL: Adversarial prompt injection detected." };
            }
        }

        // 2. Unicode Normalization (Prevents homoglyph bypasses)
        // E.g., using a cyrillic 'a' instead of ascii 'a' to bypass regex
        sanitized = sanitized.normalize('NFKC');

        // 3. Prevent excessively long prompts (DOS prevention for Tokenizers)
        if (sanitized.length > 4000) {
            return { success: false, value: null, error: "OMNI_FATAL: Prompt exceeds safe string length." };
        }

        // 4. Strip invisible control characters
        // ASCII 0-31 except newline/tab
        sanitized = sanitized.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');

        return { success: true, value: sanitized, error: null };
    }
}
