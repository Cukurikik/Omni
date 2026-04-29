using System;

namespace Omni.Business.CasimirEffectVacuumHarvester
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class StructuralIntegrity
    {
        public OmniResult<bool> EvaluateCantileverStress(double casimir_force_newtons, double material_yield_strength_newtons)
        {
            if (casimir_force_newtons < 0 || material_yield_strength_newtons <= 0)
            {
                return new OmniResult<bool>(new ArgumentException("Forces must be positive"));
            }

            // Material Science Business Logic: Nano-structural Collapse
            // The Casimir force grows exponentially stronger (1/d^4) as the plates get closer.
            // If they get too close, the vacuum force will overcome the physical strength of the
            // graphene cantilever, causing the plates to violently slam together and weld shut (stiction).
            
            if (casimir_force_newtons >= material_yield_strength_newtons * 0.95)
            {
                // Safety factor of 5%
                return new OmniResult<bool>(false); // Impending stiction collapse. Halt harvesting.
            }
            
            return new OmniResult<bool>(true); // Oscillation nominal. Continual energy extraction safe.
        }
    }
}
