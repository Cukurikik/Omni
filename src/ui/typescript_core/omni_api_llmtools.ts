// Omni API for LLM Tools Memory Calculator
export interface LLMMemoryRequirement {
    parameters_gb: number;
    kv_cache_gb: number;
    total_required_gb: number;
}

export class OmniLLMToolsAPI {
    static calculateDeploymentMemory(paramsBillion: number, seqLen: number, batch: number): LLMMemoryRequirement {
        const paramGb = paramsBillion * 2.0; // Assume fp16
        // Heuristic KV cache based on seq len and batch
        const kvGb = (seqLen * batch * 2 * 128 * 40 * 2) / (1024 * 1024 * 1024);
        
        return {
            parameters_gb: parseFloat(paramGb.toFixed(2)),
            kv_cache_gb: parseFloat(kvGb.toFixed(2)),
            total_required_gb: parseFloat((paramGb + kvGb).toFixed(2))
        };
    }
}
