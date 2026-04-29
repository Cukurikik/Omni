// OMNI Domain Layer - Ray Scaling Policy
namespace Omni.Domain.Ray {
    public enum ScaleError { None, ExceedsMaxQuota }

    public class Result<T> {
        public T Value { get; }
        public ScaleError Error { get; }
        public bool IsOk => Error == ScaleError.None;

        public Result(T value) { Value = value; Error = ScaleError.None; }
        public Result(ScaleError error) { Error = error; }
    }

    public class ClusterPolicy {
        public Result<bool> ValidateReplicaRequest(int requested, int maxAllowed) {
            if (requested > maxAllowed) {
                return new Result<bool>(ScaleError.ExceedsMaxQuota);
            }
            return new Result<bool>(true);
        }
    }
}
