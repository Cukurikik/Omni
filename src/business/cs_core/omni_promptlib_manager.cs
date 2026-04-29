// Omni Promptlib Manager (C#)
// Business Layer: Enterprise prompt storage and retrieval with strong validation.

using System;

namespace Omni.Promptlib
{
    public class PromptResult
    {
        public bool Success { get; }
        public string Content { get; }
        public string Error { get; }

        private PromptResult(bool success, string content, string error)
        {
            Success = success;
            Content = content;
            Error = error;
        }

        public static PromptResult Ok(string content) => new PromptResult(true, content, null);
        public static PromptResult Err(string error) => new PromptResult(false, null, error);
    }

    public static class PromptManager
    {
        public static PromptResult SanitizeAndStore(string rawPrompt)
        {
            if (string.IsNullOrWhiteSpace(rawPrompt))
            {
                return PromptResult.Err("Prompt cannot be empty or whitespace.");
            }

            if (rawPrompt.Contains("<script>"))
            {
                return PromptResult.Err("Prompt contains forbidden injection vectors.");
            }

            return PromptResult.Ok(rawPrompt.Trim());
        }
    }
}
