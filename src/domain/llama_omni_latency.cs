// OMNI Domain Layer - LLaMA-Omni Latency
namespace Omni.Domain.LLaMAOmni {
    public enum LatencyError { None, TooSlow }

    public class Result<T> {
        public T Value { get; }
        public LatencyError Error { get; }
        public bool IsOk => Error == LatencyError.None;

        public Result(T value) { Value = value; Error = LatencyError.None; }
        public Result(LatencyError error) { Error = error; }
    }

    public class LatencyValidator {
        public Result<bool> ValidateSpeechToSpeechLatency(double latencyMs) {
            if (latencyMs > 226.0) { // OMNI framework paper threshold
                return new Result<bool>(LatencyError.TooSlow);
            }
            return new Result<bool>(true);
        }
    }
}
