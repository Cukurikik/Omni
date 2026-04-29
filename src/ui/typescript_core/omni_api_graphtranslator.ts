export interface GraphNode {
    id: string;
    features: number[];
}

export class OmniGraphTranslatorAPI {
    /** OMNI Interface Layer: GraphTranslator API */
    public static validateNodeDim(node: GraphNode, expectedDim: number): boolean {
        return node.features.length === expectedDim;
    }
}
