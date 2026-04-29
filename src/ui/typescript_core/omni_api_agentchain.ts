export class OmniAgentChainAPI {
    public static priority(urgency: number, importance: number, wu = 0.6, wi = 0.4): number {
        return wu * urgency + wi * importance;
    }
}
