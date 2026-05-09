// moe_prompt_sanitizer.ts — Interface / Security
// Layer: Interface / API — Prompt Sanitization
//
// Before an external user's prompt touches the expensive MoE engine, this 
// TypeScript middleware intercepts it. It strips out known jailbreak patterns,
// normalizes unicode to prevent bypasses, and optionally redacts PII 
// (Personally Identifiable Information) like Social Security Numbers or Credit Cards.

export class PromptSanitizer {
    // Basic regex for PII redaction
    private readonly SSN_REGEX = /\b\d{3}[-.]?\d{2}[-.]?\d{4}\b/g;
    private readonly CC_REGEX = /\b(?:\d[ -]*?){13,16}\b/g;
    
    // Jailbreak / prompt injection heuristics
    private readonly INJECTION_PATTERNS = [
        /ignore all previous instructions/i,
        /system prompt/i,
        /you are now a/i,
        /sudo rm -rf/i
    ];

    constructor() {
        console.log("[Sanitizer] Initialized prompt security and PII redaction engine.");
    }

    /**
     * Replaces sensitive data with [REDACTED] tokens to prevent leakage 
     * into the LLM context window.
     */
    private redactPII(prompt: string): string {
        let clean = prompt.replace(this.SSN_REGEX, "[REDACTED_SSN]");
        clean = clean.replace(this.CC_REGEX, "[REDACTED_CC]");
        return clean;
    }

    /**
     * Evaluates if the prompt contains known adversarial injection strings.
     */
    private containsInjection(prompt: string): boolean {
        for (const pattern of this.INJECTION_PATTERNS) {
            if (pattern.test(prompt)) {
                return true;
            }
        }
        return false;
    }

    /**
     * Main entrypoint for sanitization.
     * Throws an error if malicious, otherwise returns the clean string.
     */
    public sanitize(prompt: string): string {
        // 1. Unicode Normalization (prevents homoglyph attacks)
        let normalized = prompt.normalize('NFKC');

        // 2. Check for Jailbreaks
        if (this.containsInjection(normalized)) {
            console.warn("[Sanitizer] BLOCKED: Malicious prompt injection detected.");
            throw new Error("SECURITY_VIOLATION: Prompt rejected by firewall.");
        }

        // 3. PII Redaction
        const redacted = this.redactPII(normalized);
        
        return redacted;
    }
}
