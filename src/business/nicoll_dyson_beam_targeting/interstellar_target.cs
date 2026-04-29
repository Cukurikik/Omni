using System;

namespace Omni.Business.NicollDysonBeamTargeting
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class InterstellarTarget
    {
        public OmniResult<string> ConfirmFiringSolution(double target_distance_lightyears, bool inhabited_system)
        {
            if (target_distance_lightyears < 0)
            {
                return new OmniResult<string>(new ArgumentException("Invalid target distance"));
            }

            // Exopolitics Business Logic: Interstellar Firing Authorization
            // Firing a Nicoll-Dyson beam is a civilization-ending event.
            // It takes years for the beam to reach its target. We must ensure
            // the target is valid and complies with the Omni Galactic Treaty.
            
            if (inhabited_system)
            {
                return new OmniResult<string>("AUTHORIZATION_DENIED: Target system is inhabited. Firing a Class-A stellar laser at a populated system violates Directive 7. Weapon system locked.");
            }
            
            if (target_distance_lightyears > 10000.0)
            {
                 return new OmniResult<string>("SOLUTION_UNSTABLE: Target exceeds 10,000 lightyears. Beam divergence will cause unacceptable collateral damage to neighboring systems. Reduce power or select closer target.");
            }
            
            return new OmniResult<string>("FIRING_SOLUTION_LOCKED: Target confirmed uninhabited. Alignment complete. Awaiting final firing sequence.");
        }
    }
}
