// OMNI Domain Layer - LiGO Growth Policy
namespace Omni.Domain.LiGO {
    public enum PolicyError { None, InvalidGrowthRatio }

    public class Result<T> {
        public T Value { get; }
        public PolicyError Error { get; }
        public bool IsOk => Error == PolicyError.None;

        public Result(T value) { Value = value; Error = PolicyError.None; }
        public Result(PolicyError error) { Error = error; }
    }

    public class GrowthValidator {
        public Result<bool> ValidateWidthExpansion(int oldWidth, int newWidth) {
            if (newWidth <= oldWidth || newWidth > oldWidth * 4) {
                return new Result<bool>(PolicyError.InvalidGrowthRatio);
            }
            return new Result<bool>(true);
        }
    }
}
