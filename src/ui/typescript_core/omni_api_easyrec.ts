export interface RecommendationRequest {
    userId: string;
    history: string[];
    topK: number;
}

export class OmniEasyRecAPI {
    /** OMNI Interface Layer: EasyRec API */
    public static validateRequest(req: RecommendationRequest): boolean {
        return req.userId.length > 0 && req.topK > 0 && req.topK <= 100;
    }

    public static formatResponse(items: string[]): string {
        return items.map((item, idx) => `${idx + 1}. ${item}`).join('\n');
    }
}
