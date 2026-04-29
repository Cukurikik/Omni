// OMNI Domain Layer - LLM Dataset Schema
using System;

namespace Omni.Domain.OpenLLMDatasets {
    public enum SchemaError { None, InvalidFormat, MissingFields }

    public class Result<T> {
        public T Value { get; }
        public SchemaError Error { get; }
        public bool IsOk => Error == SchemaError.None;

        public Result(T value) { Value = value; Error = SchemaError.None; }
        public Result(SchemaError error) { Error = error; }
    }

    public record DatasetEntry(string Instruction, string Output, string Context);

    public class DatasetValidator {
        public Result<DatasetEntry> Validate(DatasetEntry entry) {
            if (string.IsNullOrWhiteSpace(entry.Instruction) || string.IsNullOrWhiteSpace(entry.Output)) {
                return new Result<DatasetEntry>(SchemaError.MissingFields);
            }
            return new Result<DatasetEntry>(entry);
        }
    }
}
