using System;

namespace Omni.Business.KardashevTypeIvOmniGrid
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class HeatDeathMitigation
    {
        public OmniResult<string> EvaluateUniversalEntropy(double dark_energy_harvested_yw, double universal_entropy_increase_rate)
        {
            if (dark_energy_harvested_yw < 0 || universal_entropy_increase_rate < 0)
            {
                return new OmniResult<string>(new ArgumentException("Invalid thermodynamic parameters"));
            }

            // Eschatology Business Logic: Heat Death Mitigation
            // The ultimate fate of the universe is the "Heat Death" (maximum entropy),
            // where no usable energy remains. By harvesting Dark Energy and converting it
            // into usable work, a Type IV civilization attempts to artificially lower
            // the entropy of the universe, fighting back against the Second Law of Thermodynamics.
            
            // Assume 1 YW of dark energy converted = X reduction in entropy rate
            double entropy_reduction = dark_energy_harvested_yw * 1e-10; 
            
            double net_entropy_rate = universal_entropy_increase_rate - entropy_reduction;
            
            if (net_entropy_rate > 0)
            {
                return new OmniResult<string>("ENTROPY_RISING: Dark energy harvesting insufficient. The universe is still cooling towards absolute zero. Deploy more Void Harvesters to prevent Heat Death.");
            }
            
            return new OmniResult<string>("NEGUENTROPY_ACHIEVED: Harvesting rate exceeds natural entropy increase. The Heat Death of the universe has been successfully reversed. Eternity secured.");
        }
    }
}
