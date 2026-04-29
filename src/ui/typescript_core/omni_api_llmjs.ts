export interface LLMResponse {
    text: string;
    tokens: number;
}

export class OmniLLMJSAPI {
    /** OMNI Interface Layer: Universal LLM.js API */
    public static extractContent(rawResponse: any, provider: string): LLMResponse {
        try {
            if (provider === 'openai') {
                return { text: rawResponse.choices[0].message.content, tokens: rawResponse.usage.total_tokens };
            }
            if (provider === 'anthropic') {
                return { text: rawResponse.completion, tokens: 0 };
            }
            return { text: String(rawResponse), tokens: 0 };
        } catch (e) {
            return { text: "Error extracting content", tokens: 0 };
        }
    }
}
