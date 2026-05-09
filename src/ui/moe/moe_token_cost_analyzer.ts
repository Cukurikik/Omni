// moe_token_cost_analyzer.ts — Interface / UI
// Layer: Interface / Frontend — Pre-flight Cost Analysis
//
// A utility utilized by the TypeScript dashboard to analyze a prompt's length
// and estimate the billing cost based on the tenant's current tier and the 
// likely experts that will be activated.

export class TokenCostAnalyzer {
    private readonly CHARS_PER_TOKEN_ESTIMATE = 4.0;
    
    // Costs in USD per 1000 tokens based on moe_tenant_billing_worker.rb
    private readonly RATES = {
        standard: 0.10,
        premium: 0.50,
        enterprise: 2.00
    };

    constructor() {
        console.log("[Cost Analyzer] Initialized client-side cost estimation engine.");
    }

    /**
     * Roughly estimates the number of tokens in a prompt string.
     */
    public estimateTokenCount(prompt: string): number {
        return Math.ceil(prompt.length / this.CHARS_PER_TOKEN_ESTIMATE);
    }

    /**
     * Estimates the cost of the prompt BEFORE sending it to the MoE Gateway.
     */
    public estimateCost(prompt: string, expectedTier: 'standard' | 'premium' | 'enterprise'): number {
        const tokenCount = this.estimateTokenCount(prompt);
        const ratePer1k = this.RATES[expectedTier];
        
        const estimatedCost = (tokenCount / 1000.0) * ratePer1k;
        
        console.log(`[Cost Analyzer] Prompt Length: ${prompt.length} chars -> ~${tokenCount} tokens.`);
        console.log(`[Cost Analyzer] Expected Tier: ${expectedTier.toUpperCase()}. Est Cost: $${estimatedCost.toFixed(4)}`);
        
        return estimatedCost;
    }

    /**
     * Determines if the prompt exceeds a safe budget threshold to prevent bill shock.
     */
    public isWithinBudget(prompt: string, maxBudgetUsd: number, expectedTier: 'standard' | 'premium' | 'enterprise'): boolean {
        const cost = this.estimateCost(prompt, expectedTier);
        return cost <= maxBudgetUsd;
    }
}
