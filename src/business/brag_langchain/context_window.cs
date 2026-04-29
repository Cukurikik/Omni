using System;
using System.Collections.Generic;
using System.Text;

namespace Omni.Business.BragLangchain
{
    /// <summary>
    /// OMNI bRAG-langchain: Context Window Manager
    /// C# Domain logic for intelligent sliding windows and token management in Agentic RAG.
    /// Source: bragai/bRAG-langchain
    /// </summary>
    
    public class ContextError : Exception
    {
        public ContextError(string message) : base(message) {}
    }

    public class WindowResult
    {
        public string Text { get; }
        public int TokenCount { get; }
        public string ErrorMessage { get; }
        public bool IsSuccess => string.IsNullOrEmpty(ErrorMessage);

        private WindowResult(string text, int tokens, string error)
        {
            Text = text;
            TokenCount = tokens;
            ErrorMessage = error;
        }

        public static WindowResult Ok(string text, int tokens) => new WindowResult(text, tokens, null);
        public static WindowResult Fail(string error) => new WindowResult(null, 0, error);
    }

    public class ContextWindowManager
    {
        private readonly int _maxTokens;
        private readonly int _overlapTokens;

        public ContextWindowManager(int maxTokens = 4096, int overlapTokens = 200)
        {
            _maxTokens = maxTokens;
            _overlapTokens = overlapTokens;
        }

        /// <summary>
        /// Highly simplified token estimation (1 token ~= 4 chars)
        /// In production, this integrates with BPE tokenizers (tiktoken) via FFI.
        /// </summary>
        private int EstimateTokens(string text)
        {
            if (string.IsNullOrEmpty(text)) return 0;
            return text.Length / 4;
        }

        /// <summary>
        /// Packs retrieved documents into the context window up to the token limit.
        /// Prioritizes documents sequentially (assuming they are pre-ranked).
        /// </summary>
        public WindowResult PackContext(string systemPrompt, string userQuery, List<string> rankedDocuments)
        {
            int baseTokens = EstimateTokens(systemPrompt) + EstimateTokens(userQuery) + 50; // 50 for formatting overhead
            
            if (baseTokens >= _maxTokens)
            {
                return WindowResult.Fail("System prompt and user query exceed maximum context window length.");
            }

            int availableTokens = _maxTokens - baseTokens;
            int currentTokens = 0;
            StringBuilder contextBuilder = new StringBuilder();

            foreach (var doc in rankedDocuments)
            {
                int docTokens = EstimateTokens(doc);
                
                // If the whole document fits
                if (currentTokens + docTokens <= availableTokens)
                {
                    contextBuilder.AppendLine(doc);
                    contextBuilder.AppendLine("---");
                    currentTokens += docTokens;
                }
                else
                {
                    // Strict cutoff: we don't partial-pack here to preserve semantic integrity
                    // We just stop adding documents.
                    break;
                }
            }

            return WindowResult.Ok(contextBuilder.ToString(), baseTokens + currentTokens);
        }
    }
}
