using System;
using System.Collections.Generic;

namespace Omni.Business.PerformanceProfilerAgent
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class BigOEstimation
    {
        public OmniResult<string> EstimateComplexity(List<int> input_sizes, List<long> execution_times)
        {
            if (input_sizes.Count < 2 || input_sizes.Count != execution_times.Count)
            {
                return new OmniResult<string>(new ArgumentException("Insufficient or mismatched data points"));
            }

            // Profiler Business Logic: Big-O Complexity Estimation
            // Heuristically determines if an algorithm is O(1), O(N), or O(N^2) based on scaling behavior
            
            double growth_ratio = (double)execution_times[execution_times.Count - 1] / execution_times[0];
            double input_ratio = (double)input_sizes[input_sizes.Count - 1] / input_sizes[0];
            
            if (growth_ratio <= 1.5)
            {
                return new OmniResult<string>("O(1) Constant");
            }
            else if (growth_ratio <= input_ratio * 1.5)
            {
                return new OmniResult<string>("O(N) Linear");
            }
            else
            {
                return new OmniResult<string>("O(N^2) Quadratic or Worse");
            }
        }
    }
}
