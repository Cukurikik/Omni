export interface MCTSNode {
    visits: number;
    wins: number;
    children: number;
}

export class OmniAlphaZeroAPI {
    /** OMNI Interface: AlphaZero MCTS API */
    public static ucb1(node: MCTSNode, parentVisits: number, c: number = 1.41): number {
        if (node.visits <= 0) return Infinity;
        return (node.wins / node.visits) + c * Math.sqrt(Math.log(parentVisits) / node.visits);
    }
}
