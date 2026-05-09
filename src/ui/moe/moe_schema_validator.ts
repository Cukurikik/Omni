// moe_schema_validator.ts — Interface / API
// Layer: Interface / API — Strict Zod Schema Validation
//
// The Go gateway is strongly typed, but web clients send arbitrary JSON.
// This TypeScript module enforces extreme type safety at the frontend/BFF layer
// using Zod, ensuring the MoE engine is never hit with malformed configurations
// (like setting temperature to 900.0).

import { z } from "zod";

// Define the absolute limits of the MoE engine
export const MoEInferenceRequestSchema = z.object({
    prompt: z.string()
        .min(1, "Prompt cannot be empty")
        .max(128000, "Prompt exceeds maximum 128k context window limit"),
    
    expert_override: z.number().int().min(0).max(64).optional()
        .describe("Optionally force the router to use a specific expert ID"),
    
    generation_config: z.object({
        temperature: z.number()
            .min(0.0, "Temperature cannot be negative")
            .max(2.0, "Temperature > 2.0 causes catastrophic collapse")
            .default(0.7),
        
        top_p: z.number()
            .min(0.01)
            .max(1.0)
            .default(0.9),
            
        max_tokens: z.number().int()
            .min(1)
            .max(8192, "Cannot generate more than 8192 tokens in a single request")
            .default(1024),
            
        stop_sequences: z.array(z.string().max(20)).max(4).optional(),
        
        stream: z.boolean().default(true)
    }).default({})
});

// Extract the inferred TypeScript type
export type MoEInferenceRequest = z.infer<typeof MoEInferenceRequestSchema>;

export class RequestValidator {
    constructor() {
        console.log("[Zod Validator] Initialized strict schema boundaries for API requests.");
    }

    /**
     * Parses and validates raw JSON against the MoE constraints.
     * Throws a detailed ZodError if validation fails.
     */
    public validateOrThrow(rawJson: unknown): MoEInferenceRequest {
        try {
            // .parse strips out any extra undocumented JSON keys automatically
            const validData = MoEInferenceRequestSchema.parse(rawJson);
            return validData;
        } catch (error) {
            if (error instanceof z.ZodError) {
                console.error("[Zod Validator] Request rejected:", error.errors);
            }
            throw error;
        }
    }
}
