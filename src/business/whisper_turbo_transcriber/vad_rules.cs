using System;

namespace Omni.Business.WhisperTurbo
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class VadRules
    {
        public OmniResult<string> EvaluateSpeechSegment(double voice_prob, double duration_sec, double silence_threshold_sec)
        {
            if (voice_prob < 0.0 || voice_prob > 1.0)
            {
                return new OmniResult<string>(new ArgumentException("VAD probability must be between 0.0 and 1.0"));
            }

            if (duration_sec < 0.0)
            {
                return new OmniResult<string>(new ArgumentException("Segment duration cannot be negative"));
            }

            // Voice Activity Detection Business Rules
            if (voice_prob < 0.4)
            {
                if (duration_sec > silence_threshold_sec)
                {
                    return new OmniResult<string>("TRUNCATE_SILENCE");
                }
                return new OmniResult<string>("IGNORE_NOISE");
            }

            if (duration_sec > 30.0)
            {
                return new OmniResult<string>("FORCE_CHUNK_SPLIT"); // Whisper has a 30s context window limit
            }

            return new OmniResult<string>("PROCESS_TRANSCRIPTION");
        }
    }
}
