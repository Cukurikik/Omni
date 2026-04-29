export interface ReviewDecision {
    reviewerId: string;
    score: number;
    weight: number;
}

export class OmniAgentReviewAPI {
    public static aggregate(reviews: ReviewDecision[]): number {
        const tw = reviews.reduce((s, r) => s + r.weight, 0);
        if (tw <= 0) return 0;
        return reviews.reduce((s, r) => s + r.score * r.weight, 0) / tw;
    }
}
