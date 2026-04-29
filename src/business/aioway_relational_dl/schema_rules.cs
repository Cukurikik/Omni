using System;

namespace Omni.Business.AiowayRelationalDl
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class SchemaRules
    {
        public OmniResult<bool> ValidateRelationalJoin(string parent_key, string child_fkey, bool is_acyclic)
        {
            if (string.IsNullOrEmpty(parent_key) || string.IsNullOrEmpty(child_fkey))
            {
                return new OmniResult<bool>(new ArgumentException("Primary and Foreign keys must be defined for Relational DL"));
            }

            // Aioway Business Logic: Deep Learning on relational tables requires Directed Acyclic Graph (DAG) structures
            // to properly backpropagate without infinite cycles.
            if (!is_acyclic)
            {
                return new OmniResult<bool>(new InvalidOperationException("Relational schema contains cycles. Backpropagation DAG cannot be constructed."));
            }

            return new OmniResult<bool>(true);
        }
    }
}
