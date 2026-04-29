// OMNI Interface Layer: BLEU score brevity penalty
export interface llmebenchRequest {
    id: string;
    payload: Uint8Array;
}

export interface llmebenchResponse {
    success: boolean;
    error?: string;
}

export class llmebenchAPI {
    public async process(req: llmebenchRequest): Promise<llmebenchResponse> {
        if (!req || req.payload.length === 0) {
            return { success: false, error: "Empty payload" };
        }

        return {
            success: true
        };
    }
}