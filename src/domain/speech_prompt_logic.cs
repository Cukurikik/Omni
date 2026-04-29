// OMNI Domain Layer - SpeechPrompt Logic
namespace Omni.Domain.SpeechPrompt {
    public enum SpeechError { None, InvalidDuration, SilenceDetected }

    public class Result<T> {
        public T Value { get; }
        public SpeechError Error { get; }
        public bool IsOk => Error == SpeechError.None;

        public Result(T value) { Value = value; Error = SpeechError.None; }
        public Result(SpeechError error) { Error = error; }
    }

    public record AudioMetadata(string Id, double DurationMs, bool IsVoiceActive);

    public class SpeechValidator {
        public Result<AudioMetadata> Validate(AudioMetadata meta) {
            if (meta.DurationMs <= 0 || meta.DurationMs > 60000) {
                return new Result<AudioMetadata>(SpeechError.InvalidDuration);
            }
            if (!meta.IsVoiceActive) {
                return new Result<AudioMetadata>(SpeechError.SilenceDetected);
            }
            return new Result<AudioMetadata>(meta);
        }
    }
}
