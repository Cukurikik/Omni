export class OmniAgentLTSAPI {
    public static decay(strength: number, timeDelta: number, rate: number): number {
        return strength * Math.exp(-rate * timeDelta);
    }
    public static consolidate(shortTerm: number, longTerm: number, alpha: number): number {
        return alpha * shortTerm + (1 - alpha) * longTerm;
    }
}
