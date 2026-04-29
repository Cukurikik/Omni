// OMNI Domain Layer - Whisper Transcription Schema
namespace Omni.Domain.Whisper {
    public enum TranscribeError { None, EmptyAudio }

    public class Result<T> {
        public T Value { get; }
        public TranscribeError Error { get; }
        public bool IsOk => Error == TranscribeError.None;

        public Result(T value) { Value = value; Error = TranscribeError.None; }
        public Result(TranscribeError error) { Error = error; }
    }

    public class TranscriptionValidator {
        public Result<bool> ValidateOutputSegment(string text, double start, double end) {
            if (start < 0 || end <= start) {
                return new Result<bool>(TranscribeError.EmptyAudio);
            }
            return new Result<bool>(true);
        }
    }
}
