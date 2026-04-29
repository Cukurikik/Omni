// Omni InstructRAG Pipeline Manager (TypeScript)
// Domain Layer: RAG pipeline orchestration with rationale tracking.
// Ref: weizhepei/InstructRAG — ICLR 2025
interface RAGPipelineConfig { topK: number; rationaleMode: 'self_synthesized' | 'direct'; }
interface RAGResult { queryHash: string; docsRetrieved: number; rationaleGenerated: boolean; }
export function createPipeline(config: RAGPipelineConfig): RAGPipelineConfig {
  return { topK: Math.max(1, Math.min(100, config.topK)), rationaleMode: config.rationaleMode };
}
export function validateResult(result: RAGResult): boolean {
  return result.docsRetrieved > 0 && result.queryHash.length > 0;
}
