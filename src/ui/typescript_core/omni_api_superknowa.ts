export interface RAGRequest {
    query: string;
    pipelineId: string;
}

export class OmniSuperKnowaAPI {
    /** OMNI Interface Layer: SuperKnowa API */
    public static executePipeline(req: RAGRequest): string {
        return `Executing Enterprise RAG [${req.pipelineId}] for query: ${req.query}`;
    }
}
