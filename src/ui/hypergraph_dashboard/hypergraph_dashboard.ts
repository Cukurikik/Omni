export class HypergraphUIError extends Error {
    constructor(message: string) {
        super(`Hypergraph UI Error: ${message}`);
        this.name = "HypergraphUIError";
    }
}

export class Result<T> {
    constructor(public readonly value: T | null, public readonly error: Error | null = null) {}

    isOk(): boolean {
        return this.error === null;
    }

    unwrap(): T {
        if (!this.isOk()) {
            throw this.error;
        }
        return this.value as T;
    }
}

/**
 * OMNI Engine: hypergraph-dash
 * Force-directed placement limits mapping for non-euclidean hyperedge visualization limits.
 */
export class HypergraphDashboardEngine {
    constructor(private readonly repulsiveForceConstant: number = 8000.0) {}

    public computeNodeRepulsion(nodeA: {x: number, y: number}, nodeB: {x: number, y: number}): Result<{ force_x: number, force_y: number }> {
        try {
            const dx = nodeA.x - nodeB.x;
            const dy = nodeA.y - nodeB.y;
            const distSq = (dx * dx) + (dy * dy);

            if (distSq === 0.0) {
                // Total superposition
                return new Result({force_x: Math.random() * 10.0, force_y: Math.random() * 10.0}); 
            }

            // Coulomb's law approximation
            const force = this.repulsiveForceConstant / distSq;
            const dist = Math.sqrt(distSq);

            const force_x = force * (dx / dist);
            const force_y = force * (dy / dist);

            return new Result({ force_x, force_y });
        } catch (e: any) {
            return new Result(null, new HypergraphUIError(`Placement mapping failed: ${e.message}`));
        }
    }
}
