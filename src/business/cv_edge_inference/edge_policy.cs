using System;

namespace Omni.Business.CVEdgeInference
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class EdgePolicy
    {
        private readonly double _confidenceThreshold;
        private readonly int _maxLatencyMs;

        public EdgePolicy(double confidenceThreshold = 0.75, int maxLatencyMs = 50)
        {
            _confidenceThreshold = confidenceThreshold;
            _maxLatencyMs = maxLatencyMs;
        }

        public OmniResult<string> EvaluateInference(double confidence, int latencyMs)
        {
            if (confidence < 0.0 || confidence > 1.0)
                return new OmniResult<string>(new ArgumentException("Confidence must be between 0 and 1"));

            if (latencyMs > _maxLatencyMs)
                return new OmniResult<string>($"FRAME_DROPPED: Latency {latencyMs}ms exceeds SLA {_maxLatencyMs}ms");

            if (confidence < _confidenceThreshold)
                return new OmniResult<string>($"IGNORED: Confidence {confidence:F2} below threshold {_confidenceThreshold:F2}");

            return new OmniResult<string>("OBJECT_DETECTED_VALID");
        }
    }
}
