using System;
using System.Text.RegularExpressions;

namespace Omni.Business.TTSVocoder
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ProsodyRules
    {
        public OmniResult<double> CalculatePitchShift(string text, string punctuation)
        {
            if (string.IsNullOrWhiteSpace(text))
            {
                return new OmniResult<double>(new ArgumentException("Text cannot be empty"));
            }

            double basePitchShift = 1.0;

            // Deterministic prosody rule application
            if (punctuation == "?")
            {
                // Rising intonation for questions
                basePitchShift += 0.15;
            }
            else if (punctuation == "!")
            {
                // Higher energy/pitch for exclamations
                basePitchShift += 0.25;
            }
            else if (punctuation == ".")
            {
                // Falling intonation for statements
                basePitchShift -= 0.10;
            }

            // Capitalization check for emphasis
            if (Regex.IsMatch(text, @"^[A-Z\s]+$"))
            {
                basePitchShift += 0.1;
            }

            return new OmniResult<double>(Math.Round(basePitchShift, 3));
        }
    }
}
