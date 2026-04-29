// Omni SuperKnowa RAG Service (C#)
// Ref: ibm-self-serve-assets/SuperKnowa
namespace Omni.Business.SuperKnowa {
    public readonly struct RAGQuery { public string Query { get; init; } public int TopK { get; init; } }
    public static class OmniRAGService {
        public static int ValidateQuery(RAGQuery q) {
            if (string.IsNullOrWhiteSpace(q.Query)) return -1;
            if (q.TopK <= 0 || q.TopK > 100) return -2;
            return 0;
        }
        public static double ContextAdherence(int groundedTokens, int totalTokens) {
            return totalTokens == 0 ? 0 : (double)groundedTokens / totalTokens;
        }
    }
}
