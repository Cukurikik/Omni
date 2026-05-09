// moe_ecommerce_expert_bridge.ts — Domain / API
// Layer: Domain / Web — React E-commerce Integrator
//
// Inspired by `NirajVj/react-ecommerce`.
// This TypeScript module intercepts MoE Expert #14 (Sales / Retail) outputs
// and formats them into strict JSON payloads compatible with modern React 
// e-commerce storefronts (e.g., product cards, cart mutations).

export interface ProductRecommendation {
    productId: string;
    name: string;
    price: number;
    reasoning: string; // The LLM's persuasive explanation
    imageUrl: string;
}

export class EcommerceExpertBridge {
    constructor() {
        console.log("[E-commerce Bridge] Initialized MoE Expert #14 Retail Integrator.");
    }

    /**
     * Parses the raw text output from the LLM and extracts the structured product recommendation.
     * Often, the LLM will output reasoning followed by a JSON block.
     */
    public parseExpertRecommendation(llmOutput: string): ProductRecommendation | null {
        try {
            // Regex to extract a JSON block from the LLM text output
            const jsonMatch = llmOutput.match(/```json\n([\s\S]*?)\n```/);
            
            let jsonString = "";
            if (jsonMatch && jsonMatch[1]) {
                jsonString = jsonMatch[1];
            } else {
                // Fallback: assume the entire string is JSON if no code block
                jsonString = llmOutput;
            }

            const parsed = JSON.parse(jsonString);

            // Schema validation
            if (!parsed.productId || !parsed.name || typeof parsed.price !== 'number') {
                throw new Error("Invalid schema: Missing required product fields.");
            }

            console.log(`[E-commerce Bridge] Successfully parsed recommendation: ${parsed.name}`);
            
            return {
                productId: parsed.productId,
                name: parsed.name,
                price: parsed.price,
                reasoning: parsed.reasoning || "Based on your preferences.",
                imageUrl: parsed.imageUrl || "/placeholder.jpg"
            };

        } catch (e) {
            console.error(`[E-commerce Bridge] Failed to parse LLM output:`, e);
            return null;
        }
    }

    /**
     * Generates the system prompt to force the MoE into returning the correct format.
     */
    public buildPrompt(userQuery: string, userHistory: string[]): string {
        return `
        [SYSTEM: You are an E-commerce Sales Expert. Act as a helpful shopping assistant.]
        [USER HISTORY: ${userHistory.join(", ")}]
        [QUERY: ${userQuery}]
        
        Provide your reasoning, then output EXACTLY ONE JSON block representing the recommended product.
        Format:
        \`\`\`json
        {
          "productId": "string",
          "name": "string",
          "price": 0.00,
          "reasoning": "string",
          "imageUrl": "url"
        }
        \`\`\`
        `;
    }
}
