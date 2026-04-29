using System;

namespace Omni.Business.BcryptHasher
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class WorkFactorRules
    {
        public OmniResult<bool> ValidateCostFactor(int cost, bool is_admin_account)
        {
            // Business rule: Minimum cost factor based on account privilege
            int min_cost = is_admin_account ? 12 : 10;
            
            if (cost < min_cost)
            {
                return new OmniResult<bool>(new InvalidOperationException($"Cost factor {cost} is too low. Minimum required is {min_cost}."));
            }

            if (cost > 15)
            {
                return new OmniResult<bool>(new InvalidOperationException("Cost factor exceeds 15, causing potential DoS via CPU exhaustion."));
            }

            return new OmniResult<bool>(true);
        }
    }
}
