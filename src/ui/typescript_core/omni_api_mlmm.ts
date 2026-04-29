export interface LanguageScore {
    langCode: string;
    score: number;
}

export class OmniMLMMAPI {
    /** OMNI Interface Layer: MLMM API */
    public static aggregateScores(scores: LanguageScore[]): number {
        if (scores.length === 0) return 0;
        const total = scores.reduce((sum, s) => sum + s.score, 0);
        return total / scores.length;
    }

    public static formatReport(scores: LanguageScore[]): string {
        const avg = this.aggregateScores(scores);
        return `MLMM Average: ${avg.toFixed(2)}\n` + scores.map(s => `${s.langCode}: ${s.score}`).join('\n');
    }
}
