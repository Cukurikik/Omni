export interface HaystackNodeConfig {
    nodeType: 'Retriever' | 'Generator' | 'Reader';
    model: string;
}

export function buildPipeline(nodes: HaystackNodeConfig[]): string {
    return nodes.map(n => n.nodeType).join(" -> ");
}
