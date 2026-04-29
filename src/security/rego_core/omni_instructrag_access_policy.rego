# Omni InstructRAG Access Policy (Rego)
# Security Layer: Authorization for RAG pipeline execution.
# Ref: weizhepei/InstructRAG — ICLR 2025
package omni.instructrag.access
default allow_query = false
allow_query {
    input.user.role == "analyst"
    input.request.top_k <= 20
}
allow_query { input.user.role == "admin" }
