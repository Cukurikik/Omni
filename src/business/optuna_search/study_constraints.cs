using System;
using System.Collections.Generic;

namespace Omni.Business.OptunaSearch
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public enum StudyDirection
    {
        Minimize,
        Maximize
    }

    public class StudyConstraints
    {
        public OmniResult<bool> ValidateTrialParameter(double value, double low, double high, bool log_scale)
        {
            if (low >= high)
            {
                return new OmniResult<bool>(new ArgumentException("Low bound must be strictly less than high bound"));
            }

            if (log_scale && low <= 0)
            {
                return new OmniResult<bool>(new ArgumentException("Log scale requires strictly positive lower bound"));
            }

            if (value < low || value > high)
            {
                return new OmniResult<bool>(new ArgumentException($"Parameter {value} out of bounds [{low}, {high}]"));
            }

            return new OmniResult<bool>(true);
        }

        public OmniResult<bool> PruneTrial(double current_intermediate_value, double best_value, StudyDirection direction, double tolerance)
        {
            // Successive Halving Pruning Rule
            if (direction == StudyDirection.Minimize)
            {
                if (current_intermediate_value > best_value + tolerance) return new OmniResult<bool>(true); // Prune
            }
            else
            {
                if (current_intermediate_value < best_value - tolerance) return new OmniResult<bool>(true); // Prune
            }

            return new OmniResult<bool>(false); // Do not prune
        }
    }
}
