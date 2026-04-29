// OMNI Interface Layer: Sobel magnitude
export interface vision_agentRequest {
    id: string;
    payload: Uint8Array;
}

export interface vision_agentResponse {
    success: boolean;
    error?: string;
}

export class vision_agentAPI {
    public async process(req: vision_agentRequest): Promise<vision_agentResponse> {
        if (!req || req.payload.length === 0) {
            return { success: false, error: "Empty payload" };
        }

        return {
            success: true
        };
    }
}