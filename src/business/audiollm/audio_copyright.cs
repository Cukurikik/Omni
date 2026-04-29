using System;

namespace Omni.Business.AudioLLM
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public string Error { get; }
        public bool IsOk { get; }

        public OmniResult(T value, string error = null)
        {
            Value = value;
            Error = error;
            IsOk = error == null;
        }
    }

    public class CopyrightChecker
    {
        public OmniResult<bool> CheckCopyrightInfringement(string audioHash)
        {
            if (string.IsNullOrEmpty(audioHash))
            {
                return new OmniResult<bool>(false, "Audio hash is missing");
            }

            // Simple business logic wrapper
            bool isInfringing = false; // Logic to query database
            return new OmniResult<bool>(isInfringing);
        }
    }
}
