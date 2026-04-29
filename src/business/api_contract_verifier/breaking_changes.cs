using System;

namespace Omni.Business.APIContractVerifier
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class BreakingChanges
    {
        public OmniResult<bool> IsBreakingChange(bool field_removed, bool type_changed, bool required_added)
        {
            // API Contract Business Logic: Breaking Change Rules
            // Strict enforcement of SemVer 2.0 API compatibility policies
            
            if (field_removed)
            {
                // Removing a field that clients might depend on is a breaking change
                return new OmniResult<bool>(true);
            }
            
            if (type_changed)
            {
                // Changing string to int is a breaking change
                return new OmniResult<bool>(true);
            }
            
            if (required_added)
            {
                // Adding a NEW required input field breaks existing clients
                return new OmniResult<bool>(true);
            }
            
            // Adding optional fields is safe (non-breaking)
            return new OmniResult<bool>(false);
        }
    }
}
