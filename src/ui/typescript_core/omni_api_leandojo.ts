export interface LeanGoal {
    context: string[];
    target: string;
}

export class OmniLeanDojoAPI {
    /** OMNI Interface Layer: LeanDojo API */
    public static formatGoal(goal: LeanGoal): string {
        return `${goal.context.join('\n')}\n⊢ ${goal.target}`;
    }
}
