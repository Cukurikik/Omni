// OMNI Domain Layer - Prompt Schema
using System;
using System.Collections.Generic;

namespace Omni.Domain.PromptDesk {
    public enum SchemaError { None, MissingVariables }

    public class Result<T> {
        public T Value { get; }
        public SchemaError Error { get; }
        public bool IsOk => Error == SchemaError.None;

        public Result(T value) { Value = value; Error = SchemaError.None; }
        public Result(SchemaError error) { Error = error; }
    }

    public class TemplateValidator {
        public Result<bool> ValidateRequiredVars(List<string> required, List<string> provided) {
            foreach(var req in required) {
                if (!provided.Contains(req)) {
                    return new Result<bool>(SchemaError.MissingVariables);
                }
            }
            return new Result<bool>(true);
        }
    }
}
