// Omni API for Sentiment Reasoning
export interface SentimentAnalysis {
    textId: string;
    polarity: "POSITIVE" | "NEGATIVE" | "NEUTRAL";
    score: number;
}

export class OmniSentimentAPI {
    static renderSentimentBadge(analysis: SentimentAnalysis): string {
        const color = analysis.polarity === "POSITIVE" ? "green" : 
                      analysis.polarity === "NEGATIVE" ? "red" : "gray";
        return `<badge color="${color}">${analysis.polarity} (${analysis.score.toFixed(2)})</badge>`;
    }
}
