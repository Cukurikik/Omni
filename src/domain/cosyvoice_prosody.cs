// OMNI Domain Layer - CosyVoice Prosody
namespace Omni.Domain.CosyVoice {
    public enum ProsodyError { None, InvalidSpeed }

    public class Result<T> {
        public T Value { get; }
        public ProsodyError Error { get; }
        public bool IsOk => Error == ProsodyError.None;

        public Result(T value) { Value = value; Error = ProsodyError.None; }
        public Result(ProsodyError error) { Error = error; }
    }

    public class VoiceValidator {
        public Result<bool> ValidateSpeechSpeed(double speedFactor) {
            if (speedFactor < 0.25 || speedFactor > 3.0) {
                return new Result<bool>(ProsodyError.InvalidSpeed);
            }
            return new Result<bool>(true);
        }
    }
}
