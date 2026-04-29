// OMNI MOTHER — SEMESTER 13 REMEDIATION
// Pulumi — Infrastructure Layer (OMNI Zero-Mock Implementation)
// Implements deterministic Resource State Diff engine with create/update/delete/replace semantics.
// Absorbs patterns from: github.com/pulumi/pulumi

export type ResourceState = {
    urn: string;
    type: string;
    inputsHash: string;
    outputsHash: string;
    dependsOn: string[];
};

export type DiffOperation = "create" | "update" | "delete" | "replace" | "same";

export type DiffResult = {
    urn: string;
    operation: DiffOperation;
    reason: string;
};

export type PulumiResult<T> =
    | { value: T; isOk: true; error: null }
    | { value: null; isOk: false; error: string };

/**
 * Evaluates the diff between desired and current resource state.
 * Implements Pulumi's Step Generator logic:
 * - If current is null -> Create
 * - If desired is null -> Delete
 * - If inputsHash differs -> Update
 * - If type differs -> Replace (delete old + create new)
 * - Otherwise -> Same (no-op)
 *
 * @param desired - The resource state declared in the Pulumi program
 * @param current - The resource state from the last-known checkpoint
 * @returns DiffResult with operation and reason
 */
export function evaluateResourceDiff(
    desired: ResourceState | null,
    current: ResourceState | null
): PulumiResult<DiffResult> {
    // Create: resource exists in program but not in state
    if (desired !== null && current === null) {
        return {
            value: {
                urn: desired.urn,
                operation: "create",
                reason: "Resource not found in current state — will be created."
            },
            isOk: true,
            error: null
        };
    }

    // Delete: resource in state but not in program
    if (desired === null && current !== null) {
        return {
            value: {
                urn: current.urn,
                operation: "delete",
                reason: "Resource removed from program — will be deleted."
            },
            isOk: true,
            error: null
        };
    }

    // Both null — invalid
    if (desired === null && current === null) {
        return {
            value: null,
            isOk: false,
            error: "Pulumi diff: both desired and current state are null."
        };
    }

    // Type change -> Replace (delete + create)
    if (desired!.type !== current!.type) {
        return {
            value: {
                urn: desired!.urn,
                operation: "replace",
                reason: `Resource type changed: ${current!.type} -> ${desired!.type}`
            },
            isOk: true,
            error: null
        };
    }

    // Inputs changed -> Update
    if (desired!.inputsHash !== current!.inputsHash) {
        return {
            value: {
                urn: desired!.urn,
                operation: "update",
                reason: "Resource inputs changed — in-place update."
            },
            isOk: true,
            error: null
        };
    }

    // No changes
    return {
        value: {
            urn: desired!.urn,
            operation: "same",
            reason: "Resource unchanged — no operation needed."
        },
        isOk: true,
        error: null
    };
}

/**
 * Topologically sorts resources by dependency order for deployment.
 * Implements Kahn's algorithm on the depends_on graph.
 */
export function topologicalDeployOrder(
    resources: ResourceState[]
): PulumiResult<string[]> {
    if (resources.length === 0) {
        return { value: null, isOk: false, error: "Pulumi: empty resource list." };
    }

    const inDegree = new Map<string, number>();
    const graph = new Map<string, string[]>();

    for (const r of resources) {
        if (!inDegree.has(r.urn)) inDegree.set(r.urn, 0);
        if (!graph.has(r.urn)) graph.set(r.urn, []);
    }

    for (const r of resources) {
        for (const dep of r.dependsOn) {
            if (!graph.has(dep)) graph.set(dep, []);
            graph.get(dep)!.push(r.urn);
            inDegree.set(r.urn, (inDegree.get(r.urn) || 0) + 1);
        }
    }

    const queue: string[] = [];
    for (const [urn, deg] of inDegree.entries()) {
        if (deg === 0) queue.push(urn);
    }

    const order: string[] = [];
    while (queue.length > 0) {
        const curr = queue.shift()!;
        order.push(curr);
        for (const neighbor of (graph.get(curr) || [])) {
            const newDeg = (inDegree.get(neighbor) || 0) - 1;
            inDegree.set(neighbor, newDeg);
            if (newDeg === 0) queue.push(neighbor);
        }
    }

    if (order.length !== resources.length) {
        return { value: null, isOk: false, error: "Pulumi: circular dependency detected in resource graph." };
    }

    return { value: order, isOk: true, error: null };
}
