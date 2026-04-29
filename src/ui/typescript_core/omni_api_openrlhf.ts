export interface FeedbackResponse {
    chosen: string;
    rejected: string;
}

export class OmniOpenRLHFAPI {
    /** OMNI Interface Layer: OpenRLHF API */
    public static processFeedback(res: FeedbackResponse): boolean {
        return res.chosen.length > 0 && res.rejected.length > 0 && res.chosen !== res.rejected;
    }

    public static formatPair(res: FeedbackResponse): string {
        return `[CHOSEN]: ${res.chosen}\n[REJECTED]: ${res.rejected}`;
    }
}
