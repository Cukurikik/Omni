// OMNI Interface Layer: Mean Reciprocal Rank
export interface rag_evaluatorRequest {
    id: string;
    payload: Uint8Array;
}

export interface rag_evaluatorResponse {
    success: boolean;
    error?: string;
}

export class rag_evaluatorAPI {
    public async process(req: rag_evaluatorRequest): Promise<rag_evaluatorResponse> {
        if (!req || req.payload.length === 0) {
            return { success: false, error: "Empty payload" };
        }

        return {
            success: true
        };
    }
}