export interface MLLMContext {
    textPrompt: string;
    imageTokens: number;
}

export class OmniMLLMLearnAPI {
    /** OMNI Interface Layer: MLLM-Learning API */
    public static embedContext(ctx: MLLMContext): string {
        return `Fused context: "${ctx.textPrompt}" + ${ctx.imageTokens} IMG tokens.`;
    }
}
