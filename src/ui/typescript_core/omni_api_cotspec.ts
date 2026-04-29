export interface CoTResponse {
    reasoning: string;
    finalAnswer: string;
}

export class OmniCoTSpecAPI {
    /** OMNI Interface Layer: CoTSpec API */
    public static validateFormat(resp: CoTResponse): boolean {
        return resp.reasoning.includes('Step') && resp.finalAnswer.length > 0;
    }

    public static serializeToPrompt(resp: CoTResponse): string {
        return `Reasoning:\n${resp.reasoning}\n\nFinal Answer: ${resp.finalAnswer}`;
    }
}
