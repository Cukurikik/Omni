using System;

namespace Omni.Business.StellarNucleosynthesisSimulator
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class SupernovaCollapse
    {
        public OmniResult<string> EvaluateChandrasekharLimit(double core_mass_solar_masses, bool is_iron_core)
        {
            if (core_mass_solar_masses < 0)
            {
                return new OmniResult<string>(new ArgumentException("Mass must be positive"));
            }

            // Astrophysics Business Logic: Core-Collapse Supernova Trigger
            // A star burns elements up to Iron. Fusing Iron consumes energy rather than releasing it,
            // so outward radiation pressure drops. If the inert Iron core exceeds the Chandrasekhar limit (1.44 solar masses),
            // electron degeneracy pressure fails, gravity wins, and the star collapses at 23% the speed of light.
            
            double chandrasekhar_limit = 1.44;
            
            if (is_iron_core && core_mass_solar_masses > chandrasekhar_limit)
            {
                return new OmniResult<string>("SUPERNOVA_TRIGGERED: Core mass exceeded Chandrasekhar limit. Initiating runaway gravitational collapse to Neutron Star/Black Hole.");
            }
            
            return new OmniResult<string>("HYDROSTATIC_EQUILIBRIUM: Outward radiation pressure and electron degeneracy pressure balance gravity.");
        }
    }
}
