// OMNI Domain Layer - KAN Topology
namespace Omni.Domain.KAN {
    public enum TopologyError { None, InvalidGrid }

    public class Result<T> {
        public T Value { get; }
        public TopologyError Error { get; }
        public bool IsOk => Error == TopologyError.None;

        public Result(T value) { Value = value; Error = TopologyError.None; }
        public Result(TopologyError error) { Error = error; }
    }

    public class SplineValidator {
        public Result<bool> ValidateGridResolution(int gridG) {
            if (gridG < 3) { 
                return new Result<bool>(TopologyError.InvalidGrid);
            }
            return new Result<bool>(true);
        }
    }
}
