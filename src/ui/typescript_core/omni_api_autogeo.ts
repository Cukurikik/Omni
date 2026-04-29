export interface RewriteConfig {
    targetPersona: string;
    maxTokens: number;
}

export class OmniAutoGEOAPI {
    /** OMNI Interface Layer: AutoGEO API */
    public static generatePayload(text: string, config: RewriteConfig): string {
        return JSON.stringify({
            text: text,
            persona: config.targetPersona,
            limit: config.maxTokens
        });
    }
}
