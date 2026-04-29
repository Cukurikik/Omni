using System;

namespace Omni.Business.BTreeIndex
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class FillFactorRules
    {
        public OmniResult<bool> ValidateFillFactor(int fill_factor_pct)
        {
            // Business rule: Database B-Tree fill factor configuration SLA
            if (fill_factor_pct < 50 || fill_factor_pct > 100)
            {
                return new OmniResult<bool>(new ArgumentException("Fill factor must be between 50% and 100%"));
            }

            // Reject fill factors that are too high for write-heavy workloads (causes constant page splits)
            if (fill_factor_pct > 95)
            {
                return new OmniResult<bool>(new InvalidOperationException("Fill factor > 95% violates write SLA due to page split cascading."));
            }

            return new OmniResult<bool>(true);
        }
    }
}
