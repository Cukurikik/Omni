export interface VQARequest {
    image: Uint8Array;
    question: string;
}

export class OmniMiniGPT4API {
    /** OMNI Interface Layer: MiniGPT-4 API */
    public static query(req: VQARequest): string {
        return `Processing Q: ${req.question} on image of size ${req.image.length}`;
    }
}
