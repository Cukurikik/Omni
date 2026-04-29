export class OmniAgentOrchestratorAPI {
    public static leastLoaded(loads: number[]): number {
        if (loads.length === 0) return -1;
        return loads.indexOf(Math.min(...loads));
    }
}
