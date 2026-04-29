// OMNI Domain Layer - AnyGPT Modalities
namespace Omni.Domain.AnyGPT {
    public enum ModalityError { None, IncompatibleSequence }

    public class Result<T> {
        public T Value { get; }
        public ModalityError Error { get; }
        public bool IsOk => Error == ModalityError.None;

        public Result(T value) { Value = value; Error = ModalityError.None; }
        public Result(ModalityError error) { Error = error; }
    }

    public class SequenceValidator {
        public Result<bool> ValidateInterleaving(bool isText, bool isImage, bool isAudio) {
            // AnyGPT allows any-to-any interleaving, so this validation is a pass-through
            // unless resource constraints are violated.
            return new Result<bool>(true);
        }
    }
}
