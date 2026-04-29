using System;
using System.Collections.Generic;

namespace Omni.Business.LudwigAutoML
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class SchemaValidator
    {
        public OmniResult<bool> ValidateConfig(Dictionary<string, string> input_features, string output_feature)
        {
            if (input_features == null || input_features.Count == 0)
            {
                return new OmniResult<bool>(new ArgumentException("At least one input feature is required"));
            }

            if (string.IsNullOrEmpty(output_feature))
            {
                return new OmniResult<bool>(new ArgumentException("Output feature target must be specified"));
            }

            foreach (var kvp in input_features)
            {
                string type = kvp.Value;
                // Strict validation of allowed declarative types in Ludwig
                if (type != "text" && type != "numerical" && type != "category" && type != "binary")
                {
                    return new OmniResult<bool>(new ArgumentException($"Unsupported Ludwig feature type: {type}"));
                }
            }

            return new OmniResult<bool>(true);
        }
    }
}
