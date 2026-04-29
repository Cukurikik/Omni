using System;

namespace Omni.OpenDLLM
{
    public class OmniResult<T>
    {
        public T Value { get; set; }
        public string Error { get; set; }
        public bool IsOk => string.IsNullOrEmpty(Error);
    }

    public class TokenLimiter
    {
        public OmniResult<bool> CanGenerate(int requestedTokens, int maxLimit)
        {
            if (requestedTokens <= 0)
            {
                return new OmniResult<bool> { Error = "Tokens must be positive" };
            }

            // Enterprise C# token limiting for Open-dLLM code generation
            bool isAllowed = requestedTokens <= maxLimit;

            return new OmniResult<bool> { Value = isAllowed };
        }
    }
}
