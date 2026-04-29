// OMNI Domain Layer - Testing Framework Policy
using System;

namespace Omni.Domain.ContextCheck {
    public enum TestError { None, CoverageTooLow }

    public class Result<T> {
        public T Value { get; }
        public TestError Error { get; }
        public bool IsOk => Error == TestError.None;

        public Result(T value) { Value = value; Error = TestError.None; }
        public Result(TestError error) { Error = error; }
    }

    public class CIValidator {
        public Result<bool> ValidatePassRate(double passRate, double requiredThreshold) {
            if (passRate < requiredThreshold) {
                return new Result<bool>(TestError.CoverageTooLow);
            }
            return new Result<bool>(true);
        }
    }
}
