// OMNI MOTHER - DIVINE MEMORY INTEGRATION
// Gun Decentralized CRDT (OMNI Zero-Mock Implementation)
// Implements Conflict-Free Replicated Graph Data logic.

export class Result<T> {
  constructor(public value: T | null, public error: string | null, public isOk: boolean) {}

  static ok<T>(val: T): Result<T> {
    return new Result<T>(val, null, true);
  }

  static err<T>(err: string): Result<T> {
    return new Result<T>(null, err, false);
  }
}

export interface StateVector {
    [key: string]: number; // field -> timestamp
}

export interface GraphNode {
    id: string;
    data: any;
    state: StateVector;
}

export class CRDTGraphManager {
    /**
     * Resolves states using Highest-Wins timestamp protocol.
     */
    public HAM(local: GraphNode, incoming: GraphNode): Result<GraphNode> {
        if (!local || !incoming) {
            return Result.err("Invalid node inputs provided to HAM.");
        }
        if (local.id !== incoming.id) {
            return Result.err("Node ID mismatch.");
        }

        const mergedState: StateVector = { ...local.state };
        const mergedData: any = { ...local.data };

        for (const key of Object.keys(incoming.state)) {
            const incomingTs = incoming.state[key];
            const localTs = local.state[key] || 0;

            if (incomingTs > localTs) {
                // Incoming wins
                mergedState[key] = incomingTs;
                mergedData[key] = incoming.data[key];
            } else if (incomingTs === localTs) {
                // Lexical conflict resolution for exact same timestamp
                const inStr = JSON.stringify(incoming.data[key]);
                const locStr = JSON.stringify(local.data[key]);
                if (inStr > locStr) {
                    mergedData[key] = incoming.data[key];
                }
            }
        }

        return Result.ok({
            id: local.id,
            data: mergedData,
            state: mergedState
        });
    }
}
