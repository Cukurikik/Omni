export interface CodeRLEnvState {
    code: string;
    passedTests: number;
    totalTests: number;
}

export class OmniCodeRLAPI {
    /** OMNI Interface Layer: CodeRL API */
    public static calculateReward(state: CodeRLEnvState): number {
        if (state.totalTests === 0) return 0;
        return state.passedTests / state.totalTests;
    }

    public static isTerminal(state: CodeRLEnvState): boolean {
        return state.passedTests === state.totalTests;
    }
}
