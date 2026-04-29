export interface FusionResult {
    documentId: string;
    rrfScore: number;
}

export class OmniRAGFusionAPI {
    /** OMNI Interface Layer: RAG-Fusion API */
    public static filterTopK(results: FusionResult[], k: number): FusionResult[] {
        return results.sort((a, b) => b.rrfScore - a.rrfScore).slice(0, k);
    }
}
