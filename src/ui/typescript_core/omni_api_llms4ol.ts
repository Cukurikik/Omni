// Omni API for LLMs4OL Ontology Alignment
export interface TaxonomicRelation {
    hypernym: string;
    hyponym: string;
    confidence: number;
}

export class OmniLLMs4OLAPI {
    static formatOntologyGraph(relations: TaxonomicRelation[]): object {
        const nodes = new Set<string>();
        const edges = [];
        
        for (const rel of relations) {
            nodes.add(rel.hypernym);
            nodes.add(rel.hyponym);
            edges.push({ source: rel.hyponym, target: rel.hypernym, weight: rel.confidence });
        }
        
        return {
            nodes: Array.from(nodes).map(n => ({ id: n, label: n })),
            edges: edges
        };
    }
}
