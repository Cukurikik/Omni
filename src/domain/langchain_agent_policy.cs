// OMNI Domain Layer - Langchain Policy
using System;
using System.Collections.Generic;

namespace Omni.Domain.Langchain {
    public enum PolicyError { None, ToolRestricted }

    public class Result<T> {
        public T Value { get; }
        public PolicyError Error { get; }
        public bool IsOk => Error == PolicyError.None;

        public Result(T value) { Value = value; Error = PolicyError.None; }
        public Result(PolicyError error) { Error = error; }
    }

    public class ToolPolicy {
        public Result<bool> ValidateToolAccess(string toolName, List<string> allowedTools) {
            if (!allowedTools.Contains(toolName)) {
                return new Result<bool>(PolicyError.ToolRestricted);
            }
            return new Result<bool>(true);
        }
    }
}
