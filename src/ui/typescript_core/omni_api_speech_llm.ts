// OMNI Interface Layer: MFCC pre-emphasis
export interface speech_llmRequest {
    id: string;
    payload: Uint8Array;
}

export interface speech_llmResponse {
    success: boolean;
    error?: string;
}

export class speech_llmAPI {
    public async process(req: speech_llmRequest): Promise<speech_llmResponse> {
        if (!req || req.payload.length === 0) {
            return { success: false, error: "Empty payload" };
        }

        return {
            success: true
        };
    }
}