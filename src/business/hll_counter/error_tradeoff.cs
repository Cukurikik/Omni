using System;

namespace Omni.Business.HllCounter
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ErrorTradeoff
    {
        public OmniResult<double> CalculateStandardError(int register_bits_p)
        {
            if (register_bits_p < 4 || register_bits_p > 18)
            {
                return new OmniResult<double>(new ArgumentException("Precision parameter 'p' must be between 4 and 18 for HyperLogLog"));
            }

            // HLL standard error formula: 1.04 / sqrt(m), where m = 2^p
            int m = 1 << register_bits_p;
            double standard_error = 1.04 / Math.Sqrt(m);

            return new OmniResult<double>(standard_error);
        }
    }
}
