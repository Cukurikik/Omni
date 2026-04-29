export interface RecSysRequest {
    userId: string;
    context: string;
}

export class OmniLLMRecSysAPI {
    /** OMNI Interface Layer: LLM RecSys API */
    public static buildPrompt(req: RecSysRequest): string {
        return `[User: ${req.userId}] Given context: ${req.context}, recommend top items.`;
    }
}
