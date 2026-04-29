export interface MathProblem {
    id: string;
    expression: string;
}

export class OmniChatGLMAPI {
    /** OMNI Interface Layer: ChatGLM Math API */
    public static routeMath(prob: MathProblem): string {
        return `Evaluating [${prob.id}]: ${prob.expression}`;
    }
}
