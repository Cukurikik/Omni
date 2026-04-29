using System;

namespace Omni.Business.HiggsBosonMassModulator
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class InertialDampening
    {
        public OmniResult<string> EvaluateDampeningSafety(double baseline_mass_kg, double modulated_mass_kg)
        {
            if (baseline_mass_kg <= 0 || modulated_mass_kg <= 0)
            {
                return new OmniResult<string>(new ArgumentException("Mass must be strictly positive"));
            }

            // High-Energy Physics Business Logic: Inertial Dampening
            // If we reduce a starship's mass to near zero, it can accelerate to lightspeed instantly.
            // HOWEVER, if the mass reaches exactly zero, the ship's matter becomes pure photons (light)
            // and dissolves into radiation. We must enforce a strict lower bound on mass modulation.
            
            double min_safe_mass_ratio = 0.001; // Cannot reduce mass below 0.1% of original
            
            if ((modulated_mass_kg / baseline_mass_kg) < min_safe_mass_ratio)
            {
                return new OmniResult<string>("CATASTROPHIC_PHOTON_DISSOLUTION_RISK: Modulated mass too low. Matter will lose atomic cohesion. Scramming Higgs field generator.");
            }
            
            return new OmniResult<string>("INERTIAL_DAMPENING_ACTIVE: Ship mass reduced safely. Extreme acceleration maneuvers authorized.");
        }
    }
}
