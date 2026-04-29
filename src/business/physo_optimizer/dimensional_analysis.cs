using System;
using System.Collections.Generic;

namespace Omni.Business.PhySO
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class DimensionalAnalysis
    {
        // Business Rule: Ensure generated physical equations have consistent physical dimensions
        // e.g., cannot add Length (m) and Mass (kg).

        public OmniResult<bool> ValidateEquationDimensions(string operatorNode, string leftDim, string rightDim)
        {
            if (string.IsNullOrEmpty(operatorNode) || string.IsNullOrEmpty(leftDim) || string.IsNullOrEmpty(rightDim))
            {
                return new OmniResult<bool>(new ArgumentException("Invalid dimensional inputs"));
            }

            switch (operatorNode)
            {
                case "ADD":
                case "SUB":
                    // strict dimensional consistency required for addition/subtraction
                    if (leftDim == rightDim) return new OmniResult<bool>(true);
                    else return new OmniResult<bool>(new InvalidOperationException($"Dimensional mismatch: Cannot ADD/SUB {leftDim} and {rightDim}"));
                
                case "MUL":
                case "DIV":
                    // Multiplication/Division always allowed, results in new composite dimension
                    return new OmniResult<bool>(true);
                
                case "EXP":
                case "SIN":
                case "COS":
                    // Arguments to transcendental functions must be dimensionless
                    if (rightDim == "DIMENSIONLESS") return new OmniResult<bool>(true);
                    else return new OmniResult<bool>(new InvalidOperationException($"Transcendental argument must be dimensionless, got {rightDim}"));

                default:
                    return new OmniResult<bool>(new ArgumentException($"Unknown operator: {operatorNode}"));
            }
        }
    }
}
