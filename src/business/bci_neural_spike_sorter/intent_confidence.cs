using System;

namespace Omni.Business.BciNeuralSpikeSorter
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class IntentConfidence
    {
        public OmniResult<string> ClassifyMotorIntent(double confidence_score, double actuation_threshold)
        {
            if (confidence_score < 0 || actuation_threshold < 0 || confidence_score > 1.0)
            {
                return new OmniResult<string>(new ArgumentException("Invalid confidence scores"));
            }

            // Neural Engineering Business Logic: Motor Cortex Intent
            // If the user imagines moving their right hand, the BCI classifies the brainwaves.
            // We only actuate the robotic arm if we are highly confident; otherwise, a false positive
            // could cause the robotic arm to move erratically and injure someone.
            
            if (confidence_score >= actuation_threshold)
            {
                return new OmniResult<string>("ACTUATE_ROBOTIC_ARM: Intent confidence meets safety threshold.");
            }
            
            return new OmniResult<string>("IGNORE: Intent confidence too low. Awaiting clearer neural signal.");
        }
    }
}
