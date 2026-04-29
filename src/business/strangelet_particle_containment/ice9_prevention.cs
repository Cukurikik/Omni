using System;

namespace Omni.Business.StrangeletParticleContainment
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class Ice9Prevention
    {
        public OmniResult<string> EvaluateContainmentIntegrity(double magnetic_field_strength_tesla, bool is_vacuum_breached)
        {
            if (magnetic_field_strength_tesla < 0)
            {
                return new OmniResult<string>(new ArgumentException("Field strength cannot be negative"));
            }

            // High-Energy Physics Business Logic: Strange Matter "Ice-9" Prevention
            // Strangelets carry a negative electrical charge. We contain them inside a vacuum
            // using an immense Penning trap. If the magnetic field fails, or air enters the vacuum,
            // the strangelet will touch the containment wall. It will instantly convert the Earth
            // into a hot sphere of strange matter, destroying all life.
            
            double minimum_containment_field = 45.0; // Tesla
            
            if (is_vacuum_breached || magnetic_field_strength_tesla < minimum_containment_field)
            {
                return new OmniResult<string>("EXISTENTIAL_BREACH: Strangelet containment failed. Initiating immediate payload ejection into the Sun to prevent planetary strange-matter conversion.");
            }
            
            return new OmniResult<string>("CONTAINMENT_STABLE: Quark-gluon plasma perfectly suspended in vacuum. Earth is safe.");
        }
    }
}
