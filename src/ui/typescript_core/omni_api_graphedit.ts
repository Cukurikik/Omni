export interface GraphEdge {
    source: string;
    target: string;
}

export class OmniGraphEditAPI {
    /** OMNI Interface Layer: GraphEdit API */
    public static serializeGraph(nodes: string[], edges: GraphEdge[]): string {
        const edgeStr = edges.map(e => `${e.source}--${e.target}`).join(',');
        return `NODES:${nodes.length}|EDGES:[${edgeStr}]`;
    }

    public static parseConstraints(raw: string): GraphEdge[] {
        if (!raw) return [];
        return raw.split(',').map(pair => {
            const [u, v] = pair.split('--');
            return { source: u, target: v };
        });
    }
}
