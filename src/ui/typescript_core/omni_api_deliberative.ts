export interface DeliberationStep {
    stepId: number;
    argument: string;
}

export class OmniDeliberativeAPI {
    /** OMNI Interface Layer: Deliberative API */
    public static buildDebateTree(steps: DeliberationStep[]): string {
        return steps.map(s => `[Node ${s.stepId}]: ${s.argument}`).join(' -> ');
    }
}
