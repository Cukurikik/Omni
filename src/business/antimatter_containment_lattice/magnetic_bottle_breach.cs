using System;

namespace Omni.Business.AntimatterContainmentLattice
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class MagneticBottleBreach
    {
        public OmniResult<string> EvaluateContainmentIntegrity(double magnetic_field_tesla, double vacuum_pressure_torr)
        {
            if (magnetic_field_tesla < 0 || vacuum_pressure_torr < 0)
            {
                return new OmniResult<string>(new ArgumentException("Invalid containment metrics"));
            }

            // High-Energy Storage Business Logic: Magnetic Bottle Failure
            // Antimatter cannot touch ANY physical matter, not even the air in the room,
            // or it will detonate instantly. We suspend it in a perfect vacuum using
            // a Penning trap (magnetic bottle).
            
            // Ultra-high vacuum required (less than 1e-11 Torr)
            if (vacuum_pressure_torr > 1e-9)
            {
                return new OmniResult<string>("BREACH_WARNING: Micro-leaks detected in vacuum chamber. Stray air molecules are annihilating with the payload. Evacuate chamber immediately.");
            }
            
            if (magnetic_field_tesla < 2.0)
            {
                 return new OmniResult<string>("CRITICAL_CONTAINMENT_FAILURE: Magnetic field collapsing. Antimatter plasma is drifting toward the physical hull. Eject payload core immediately.");
            }
            
            return new OmniResult<string>("CONTAINMENT_STABLE: Positron cloud perfectly suspended in absolute vacuum.");
        }
    }
}
