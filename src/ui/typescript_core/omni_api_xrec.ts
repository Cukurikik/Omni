// Omni API for XRec Recommendation Engine
export interface RecommendationItem {
    itemId: string;
    score: number;
    explanation: string;
}

export class OmniXRecAPI {
    static formatRecommendations(items: RecommendationItem[], maxResults: number = 5): RecommendationItem[] {
        return [...items]
            .sort((a, b) => b.score - a.score)
            .slice(0, maxResults)
            .map(item => ({
                ...item,
                score: parseFloat(item.score.toFixed(4))
            }));
    }
}
