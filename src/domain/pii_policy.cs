// OMNI Domain Layer - PII Policy
namespace Omni.Domain.PIIGuard {
    public enum PolicyError { None, InvalidClassification }

    public class Result<T> {
        public T Value { get; }
        public PolicyError Error { get; }
        public bool IsOk => Error == PolicyError.None;

        public Result(T value) { Value = value; Error = PolicyError.None; }
        public Result(PolicyError error) { Error = error; }
    }

    public class ComplianceChecker {
        public Result<bool> IsCompliant(bool hasPii, string storageZone) {
            if (string.IsNullOrEmpty(storageZone)) {
                return new Result<bool>(PolicyError.InvalidClassification);
            }
            
            // If it has PII, it must be in the EU zone for GDPR
            if (hasPii && storageZone != "EU_SECURE") {
                return new Result<bool>(false);
            }
            
            return new Result<bool>(true);
        }
    }
}
