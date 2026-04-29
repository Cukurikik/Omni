using System;

namespace Omni.Business.DigitalConsciousnessSubstrateTransfer
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class IdentityContinuity
    {
        public OmniResult<string> EvaluateShipOfTheseus(double mapping_fidelity_percentage, bool destructive_scan)
        {
            if (mapping_fidelity_percentage < 0 || mapping_fidelity_percentage > 100)
            {
                return new OmniResult<string>(new ArgumentException("Invalid fidelity percentage"));
            }

            // Philosophy/Neuroscience Business Logic: Identity Continuity
            // If you copy a brain and turn it on, is it YOU or a clone?
            // "Ship of Theseus" paradox. A non-destructive scan creates a clone (divergence).
            // A gradual, destructive Moravec transfer maintains unbroken continuity of subjective experience.
            
            if (mapping_fidelity_percentage < 99.999)
            {
                return new OmniResult<string>("EGO_DEATH_WARNING: Fidelity below 99.999%. Severe memory loss and personality alteration expected. Halt transfer.");
            }
            
            if (!destructive_scan)
            {
                 return new OmniResult<string>("CLONING_VIOLATION: Non-destructive scan selected. This will result in two divergent conscious entities. The original biological entity will remain trapped in meat-space. Illegal under Omni Directive 4.");
            }
            
            return new OmniResult<string>("CONTINUITY_SECURE: Gradual destructive transfer authorized. Subjective stream of consciousness will seamlessly transition to silicon substrate.");
        }
    }
}
