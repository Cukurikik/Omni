// OMNI Domain Layer - Indian Law Rules
using System;

namespace Omni.Domain.IndianLawyerGPT {
    public enum LegalError { None, InvalidJurisdiction }

    public class Result<T> {
        public T Value { get; }
        public LegalError Error { get; }
        public bool IsOk => Error == LegalError.None;

        public Result(T value) { Value = value; Error = LegalError.None; }
        public Result(LegalError error) { Error = error; }
    }

    public class LegalValidator {
        public Result<bool> ValidateJurisdiction(string contextText) {
            if (!contextText.Contains("India") && !contextText.Contains("IPC") && !contextText.Contains("CRPC")) {
                return new Result<bool>(LegalError.InvalidJurisdiction);
            }
            return new Result<bool>(true);
        }
    }
}
