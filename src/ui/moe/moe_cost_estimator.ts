// moe_cost_estimator.ts — Domain / Analytics
// Layer: UI / Economics — Cloud Cost Prediction
//
// Calculates estimated monthly infrastructure costs for running
// a specified MoE architecture on cloud providers (AWS/GCP),
// taking into account active parameters vs total parameters.

export interface CloudInstance {
    name: string;
    vramGb: number;
    hourlyCost: number; // USD
}

export interface MoEModelConfig {
    hiddenDim: number;
    numLayers: number;
    numExperts: number;
    topK: number;
    bytesPerParam: number; // e.g., 2 for FP16
}

// AWS Mock Pricing
const INSTANCES: CloudInstance[] = [
    { name: "p4d.24xlarge (8x A100 40GB)", vramGb: 320, hourlyCost: 32.77 },
    { name: "p4de.24xlarge (8x A100 80GB)", vramGb: 640, hourlyCost: 40.96 },
    { name: "p5.48xlarge (8x H100 80GB)", vramGb: 640, hourlyCost: 98.32 }
];

export class MoECostEstimator {
    /**
     * Calculates the memory required for weights and KV cache (simplified).
     */
    static calculateVramRequirement(config: MoEModelConfig): number {
        // Standard Attention layer params ~ 4D^2
        const attnParams = 4 * Math.pow(config.hiddenDim, 2);
        
        // MoE FFN params ~ 8D^2 per expert
        const expertParams = 8 * Math.pow(config.hiddenDim, 2);
        const totalFfnParams = expertParams * config.numExperts;
        
        const paramsPerLayer = attnParams + totalFfnParams;
        const totalParams = paramsPerLayer * config.numLayers;
        
        // Return in GB
        const weightMemoryGb = (totalParams * config.bytesPerParam) / 1e9;
        
        // Add 20% overhead for KV cache and activations
        return weightMemoryGb * 1.2;
    }

    /**
     * Finds the cheapest instance configuration that can hold the model.
     */
    static estimateMonthlyCost(config: MoEModelConfig): {
        vramRequiredGb: number;
        instanceType: string;
        instanceCount: number;
        monthlyCost: number;
    } | null {
        const reqVram = this.calculateVramRequirement(config);
        
        let bestOption = null;
        let lowestCost = Infinity;

        for (const instance of INSTANCES) {
            // How many instances needed via Expert/Tensor Parallelism?
            const count = Math.ceil(reqVram / instance.vramGb);
            
            const monthlyCost = count * instance.hourlyCost * 24 * 30.5; // ~732 hours/month
            
            if (monthlyCost < lowestCost) {
                lowestCost = monthlyCost;
                bestOption = {
                    vramRequiredGb: reqVram,
                    instanceType: instance.name,
                    instanceCount: count,
                    monthlyCost: monthlyCost
                };
            }
        }

        return bestOption;
    }
}
