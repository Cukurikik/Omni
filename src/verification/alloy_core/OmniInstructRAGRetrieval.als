-- Omni InstructRAG Retrieval Model (Alloy)
-- Verification Layer: Formal model for RAG retrieval correctness.
-- Ref: weizhepei/InstructRAG — ICLR 2025
module OmniInstructRAGRetrieval
sig Document { relevance: one Int, content: one String }
sig Query { topK: one Int, results: set Document }
fact RetrievalConstraints {
  all q: Query | #q.results <= q.topK
  all q: Query, d1, d2: q.results | d1.relevance >= d2.relevance or d1 = d2
}
pred ValidRetrieval[q: Query] { #q.results > 0 and q.topK > 0 }
run ValidRetrieval for 5
