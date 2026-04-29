// ===========================================================================
// OMNI PROMPT ROUTING ENGINE (SEMESTER 5 — BATCH 6)
// ===========================================================================
// Absorbed From  : dair-ai/Prompt-Engineering-Guide
// Logic Inherited: Interface Layer (Type-Safe Prompt Construction & Injection Guard)
// ===========================================================================

export type PromptStrategy = "zero_shot" | "one_shot" | "few_shot" | "chain_of_thought";

export interface PromptPayload {
    systemDirective: string;
    userPrompt: string;
    strategy: PromptStrategy;
    temperature: number;
    maxTokens: number;
}

export class OmniPromptRoutingEngine {
    private injectionPatterns: RegExp[] = [
        /ignore\s+(all\s+)?previous\s+instructions/i,
        /you\s+are\s+now\s+/i,
        /system:\s*/i,
        /\]\]\s*\[\[/,
    ];

    constructor() {}

    public buildPrompt(userInput: string, strategy: PromptStrategy = "zero_shot", temperature: number = 0.7): { success: boolean; value?: PromptPayload; error?: Error } {
        if (!userInput || userInput.trim().length === 0) {
            return { success: false, error: new Error("User input cannot be empty.") };
        }
        if (temperature < 0 || temperature > 2) {
            return { success: false, error: new Error("Temperature must be 0.0-2.0.") };
        }
        const sanitized = this.sanitizeInput(userInput);
        if (!sanitized.success) return { success: false, error: sanitized.error };

        const payload: PromptPayload = {
            systemDirective: "You are OMNI, a helpful AI assistant.",
            userPrompt: sanitized.value!,
            strategy, temperature,
            maxTokens: strategy === "chain_of_thought" ? 2048 : 1024
        };
        return { success: true, value: payload };
    }

    public sanitizeInput(input: string): { success: boolean; value?: string; error?: Error } {
        for (const pattern of this.injectionPatterns) {
            if (pattern.test(input)) {
                return { success: false, error: new Error("Potential prompt injection detected and blocked.") };
            }
        }
        return { success: true, value: input.trim() };
    }

    public evaluateHealth(): Record<string, any> {
        return { engine: "OmniPromptRoutingEngine", layer: "Interface", status: "healthy",
                 injection_patterns: this.injectionPatterns.length,
                 learned_from: "dair-ai/Prompt-Engineering-Guide" };
    }

    // --- Registry Interface ---
    diagnostics(): Record<string, unknown> {
        return {
            engine: "OmniPromptRoutingEngine",
            version: "1.0.0",
            status: "operational",
            layer: "ui",
            language: "TypeScript",
        };
    }
}
