// OMNI MOTHER — SEMESTER 13 REMEDIATION
// GraphQL — Business Layer (OMNI Zero-Mock Implementation)
// Implements deterministic field resolver execution engine with depth limiting.
// Absorbs patterns from: github.com/graphql/graphql-js, graphql-spec

export type Result<T> =
    | { value: T; isOk: true; error: null }
    | { value: null; isOk: false; error: string };

export type FieldNode = {
    fieldName: string;
    alias?: string;
    arguments: Record<string, unknown>;
    children: FieldNode[];
};

export type ResolverMap = Record<string, (parent: unknown, args: Record<string, unknown>) => unknown>;

export type ExecutionResult = {
    data: Record<string, unknown>;
    errors: string[];
};

/**
 * Executes a GraphQL field selection set against a resolver map.
 * Implements the exact algorithm from GraphQL spec Section 6.4:
 * "Executing Selection Sets"
 *
 * @param fields    Parsed selection set as FieldNode tree
 * @param resolvers Map of typeName.fieldName -> resolver function
 * @param rootValue Initial root value passed to top-level resolvers
 * @param maxDepth  Maximum nesting depth (prevents abuse)
 * @returns ExecutionResult with data and accumulated errors
 */
export function executeFieldSelection(
    fields: FieldNode[],
    resolvers: ResolverMap,
    rootValue: unknown,
    maxDepth: number
): Result<ExecutionResult> {
    if (maxDepth <= 0) {
        return { value: null, isOk: false, error: "GraphQL: maxDepth must be > 0." };
    }

    const result: ExecutionResult = { data: {}, errors: [] };

    try {
        resolveFields(fields, resolvers, rootValue, result, 0, maxDepth);
    } catch (e) {
        return { value: null, isOk: false, error: `GraphQL execution error: ${e}` };
    }

    return { value: result, isOk: true, error: null };
}

function resolveFields(
    fields: FieldNode[],
    resolvers: ResolverMap,
    parentValue: unknown,
    result: ExecutionResult,
    currentDepth: number,
    maxDepth: number
): Record<string, unknown> {
    const output: Record<string, unknown> = {};

    for (const field of fields) {
        const responseKey = field.alias ?? field.fieldName;

        // Depth check — GraphQL spec recommends query complexity limits
        if (currentDepth >= maxDepth) {
            result.errors.push(
                `Field '${field.fieldName}' exceeds max depth of ${maxDepth}.`
            );
            output[responseKey] = null;
            continue;
        }

        // Look up resolver
        const resolverKey = field.fieldName;
        const resolver = resolvers[resolverKey];

        if (!resolver) {
            // Default field resolver: property access on parent
            if (parentValue !== null && typeof parentValue === "object") {
                output[responseKey] = (parentValue as Record<string, unknown>)[field.fieldName] ?? null;
            } else {
                output[responseKey] = null;
            }
        } else {
            try {
                const resolvedValue = resolver(parentValue, field.arguments);
                output[responseKey] = resolvedValue;

                // If field has sub-selections, recurse
                if (field.children.length > 0 && resolvedValue !== null) {
                    if (Array.isArray(resolvedValue)) {
                        // List type: resolve each item
                        output[responseKey] = resolvedValue.map((item) =>
                            resolveFields(field.children, resolvers, item, result, currentDepth + 1, maxDepth)
                        );
                    } else {
                        output[responseKey] = resolveFields(
                            field.children, resolvers, resolvedValue, result, currentDepth + 1, maxDepth
                        );
                    }
                }
            } catch (e) {
                result.errors.push(`Resolver error for '${field.fieldName}': ${e}`);
                output[responseKey] = null;
            }
        }
    }

    // Merge into result.data at top level
    if (currentDepth === 0) {
        Object.assign(result.data, output);
    }

    return output;
}

/**
 * Validates query depth does not exceed limit before execution.
 * Prevents deeply nested attacks (e.g., recursive type queries).
 */
export function validateQueryDepth(
    fields: FieldNode[],
    maxDepth: number
): Result<number> {
    function measure(nodes: FieldNode[], depth: number): number {
        if (nodes.length === 0) return depth;
        let maxFound = depth;
        for (const node of nodes) {
            const childDepth = measure(node.children, depth + 1);
            if (childDepth > maxFound) maxFound = childDepth;
        }
        return maxFound;
    }

    const actualDepth = measure(fields, 0);

    if (actualDepth > maxDepth) {
        return {
            value: null,
            isOk: false,
            error: `GraphQL query depth ${actualDepth} exceeds maximum ${maxDepth}.`
        };
    }

    return { value: actualDepth, isOk: true, error: null };
}
