// Omni API for Omni-MathEval
export interface MathChainStep {
    stepIndex: number;
    derivation: string;
    isCorrect: boolean;
}

export class OmniMathEvalAPI {
    static renderReasoningChain(steps: MathChainStep[]): string {
        return steps.map(s => {
            const icon = s.isCorrect ? "✅" : "❌";
            return `Step ${s.stepIndex}: ${s.derivation} ${icon}`;
        }).join("\\n");
    }
}
