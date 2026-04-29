using System;

namespace Omni.Business.TachyonFieldFtlCommunicator
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ParadoxResolution
    {
        public OmniResult<string> EvaluateNovikovConsistency(double backward_time_delta_years, string message_content)
        {
            if (backward_time_delta_years > 0)
            {
                return new OmniResult<string>("No causality violation detected. Message moving forward in time relative to receiver.");
            }

            // Theoretical Physics Business Logic: Novikov Self-Consistency Principle
            // If a message travels backward in time, it cannot change the past in a way that prevents
            // the message from being sent (the Grandfather Paradox).
            // The universe must enforce a consistent timeline.
            
            if (message_content.Contains("ABORT_LAUNCH"))
            {
                return new OmniResult<string>("PARADOX_DETECTED: Message attempts to alter a fixed event in the past. Quantum censorship engaged. Message blocked.");
            }
            
            return new OmniResult<string>("CONSISTENT_LOOP: Information travels backward but fulfills an already established historical event.");
        }
    }
}
