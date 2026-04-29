using System;

namespace Omni.Business.GraphRagRetriever
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ContextWindowRules
    {
        public OmniResult<int> CalculateMaxNodes(int context_window_tokens, int avg_tokens_per_node)
        {
            if (context_window_tokens <= 0 || avg_tokens_per_node <= 0)
            {
                return new OmniResult<int>(new ArgumentException("Token counts must be positive"));
            }

            // Graph RAG Business Logic: Context Window Budgeting
            // We must reserve 20% of the context window for the prompt instruction and reasoning
            
            int budget_for_rag = (int)(context_window_tokens * 0.8);
            
            int max_nodes = budget_for_rag / avg_tokens_per_node;
            
            // Hard cap to prevent excessive LLM distraction (Lost in the Middle phenomenon)
            int final_max = Math.Min(max_nodes, 50);

            return new OmniResult<int>(final_max);
        }
    }
}
