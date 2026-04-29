using System;
using System.Text;
using System.Collections.Generic;

namespace Omni.Business.RagFromScratchLlm
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class PromptFormatting
    {
        public OmniResult<string> ConstructContextPrompt(string user_query, List<string> retrieved_chunks, int max_context_chars)
        {
            if (string.IsNullOrEmpty(user_query))
            {
                return new OmniResult<string>(new ArgumentException("User query cannot be empty"));
            }

            // RAG from Scratch Business Logic: Strict Context Window Formatting
            StringBuilder prompt = new StringBuilder();
            prompt.AppendLine("System: You are a precise helpful assistant. Answer the user's query STRICTLY based on the provided context.");
            prompt.AppendLine("--- CONTEXT ---");
            
            int current_length = prompt.Length + user_query.Length + 50; // Buffer
            
            foreach (var chunk in retrieved_chunks)
            {
                if (current_length + chunk.Length > max_context_chars)
                {
                    break; // Hard cutoff to prevent LLM context overflow
                }
                prompt.AppendLine(chunk);
                current_length += chunk.Length;
            }
            
            prompt.AppendLine("--- END CONTEXT ---");
            prompt.AppendLine($"User: {user_query}");
            prompt.Append("Assistant:");

            return new OmniResult<string>(prompt.ToString());
        }
    }
}
