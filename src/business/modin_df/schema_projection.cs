using System;
using System.Collections.Generic;

namespace Omni.Business.ModinDF
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class SchemaProjection
    {
        public OmniResult<List<string>> ValidateProjection(List<string> df_columns, List<string> requested_columns)
        {
            if (requested_columns == null || requested_columns.Count == 0)
            {
                return new OmniResult<List<string>>(new ArgumentException("Requested columns cannot be empty"));
            }

            HashSet<string> available = new HashSet<string>(df_columns);
            List<string> valid_projection = new List<string>();

            foreach (var col in requested_columns)
            {
                if (!available.Contains(col))
                {
                    return new OmniResult<List<string>>(new ArgumentException($"Column not found in schema: {col}"));
                }
                valid_projection.Add(col);
            }

            return new OmniResult<List<string>>(valid_projection);
        }
    }
}
