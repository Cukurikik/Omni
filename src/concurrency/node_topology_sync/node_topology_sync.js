class TopologySyncError extends Error {
    constructor(message) {
        super(message);
        this.name = "TopologySyncError";
    }
}

class Result {
    constructor(value, error = null) {
        this.value = value;
        this.error = error;
    }

    isOk() {
        return this.error === null;
    }

    unwrap() {
        if (!this.isOk()) {
            throw this.error;
        }
        return this.value;
    }
}

/**
 * OMNI Engine: topology-sync
 * Event map divergence calculation for asynchronous graph topology updates.
 */
class NodeTopologySyncEngine {
    constructor(maxDivergenceNodes = 50) {
        this.maxDivergenceNodes = maxDivergenceNodes;
    }

    computeGraphDivergence(localNodeCount, remoteNodeCount) {
        try {
            if (localNodeCount < 0 || remoteNodeCount < 0) {
                return new Result(null, new TopologySyncError("Graph node parameters geometrically invalid"));
            }

            const divergence = Math.abs(localNodeCount - remoteNodeCount);

            if (divergence > this.maxDivergenceNodes) {
                return new Result(null, new TopologySyncError(`Topological divergence shattered (Delta ${divergence} > Limit ${this.maxDivergenceNodes})`));
            }

            return new Result({ node_divergence: divergence, requires_hard_sync: divergence > (this.maxDivergenceNodes * 0.8) });
        } catch (e) {
            return new Result(null, new TopologySyncError(`Map fault: ${e.message}`));
        }
    }

    calculateCycleTickDesync(tickA, tickB) {
        try {
             let diff = Math.abs(tickA - tickB);
             
             if (diff > 1000) {
                 return new Result(null, new TopologySyncError("Vector clocks permanently diverged across timelines"));
             }
             
             return new Result({ tick_delta: diff, is_aligned: diff === 0 });
        } catch(e) {
             return new Result(null, new TopologySyncError(`Tick fault: ${e.message}`));
        }
    }
}

module.exports = { NodeTopologySyncEngine, Result, TopologySyncError };
