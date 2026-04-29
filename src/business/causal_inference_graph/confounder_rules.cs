using System;

namespace Omni.Business.CausalInferenceGraph
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ConfounderRules
    {
        public OmniResult<bool> RequireBackdoorAdjustment(bool path_has_collider, bool path_has_confounder)
        {
            // Causal Business Logic: Backdoor Criterion Enforcement
            // Ensures LLMs do not make spurious correlations (e.g. Ice cream sales cause shark attacks)
            
            if (path_has_collider)
            {
                // Do not condition on colliders, it opens spurious paths
                return new OmniResult<bool>(false);
            }
            
            if (path_has_confounder)
            {
                // Must adjust for observed confounders to isolate causal effect
                return new OmniResult<bool>(true);
            }
            
            return new OmniResult<bool>(false);
        }
    }
}
