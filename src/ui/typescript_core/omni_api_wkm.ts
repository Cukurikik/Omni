// Omni API for WKM Planning Controller
export interface WKMStateTransition {
    fromState: string;
    action: string;
    toState: string;
    reward: number;
}

export class OmniWKMAPI {
    static traceTrajectory(transitions: WKMStateTransition[]): number {
        if (!transitions || transitions.length === 0) return 0;
        return transitions.reduce((sum, t) => sum + t.reward, 0);
    }
}
