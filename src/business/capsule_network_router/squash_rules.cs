using System;

namespace Omni.Business.CapsuleNetworkRouter
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class SquashRules
    {
        public OmniResult<bool> ValidateSquashMagnitude(double vector_magnitude)
        {
            if (vector_magnitude < 0.0)
            {
                return new OmniResult<bool>(new ArgumentException("Vector magnitude cannot be negative"));
            }

            // In Capsule Networks, the length of the activity vector represents the probability 
            // that the entity exists. Therefore, its magnitude must be strictly bound [0, 1)
            // due to the non-linear "squashing" function: ||s||^2 / (1 + ||s||^2) * s / ||s||
            
            if (vector_magnitude >= 1.0)
            {
                return new OmniResult<bool>(new InvalidOperationException("Squash function invariant violated: magnitude >= 1.0"));
            }

            return new OmniResult<bool>(true);
        }
    }
}
