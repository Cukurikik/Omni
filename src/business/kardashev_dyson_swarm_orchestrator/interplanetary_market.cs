using System;

namespace Omni.Business.KardashevDysonSwarmOrchestrator
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class InterplanetaryMarket
    {
        public OmniResult<double> CalculateExawattPricing(double total_swarm_yield_exawatts, double planetary_demand_exawatts)
        {
            if (total_swarm_yield_exawatts < 0 || planetary_demand_exawatts < 0)
            {
                return new OmniResult<double>(new ArgumentException("Energy metrics must be positive"));
            }

            // Kardashev Type-II Business Logic: Interplanetary Energy Markets
            // A Dyson Swarm harvests the entire energy output of a star.
            // We price energy dynamically based on the demands of Earth, Mars, and the asteroid mining colonies.
            
            double base_price_per_terawatt_hour = 50.0; // Intergalactic credits
            
            // Dynamic pricing based on supply/demand ratio
            double demand_ratio = planetary_demand_exawatts / Math.Max(total_swarm_yield_exawatts, 0.001);
            
            double current_market_price = base_price_per_terawatt_hour * Math.Pow(demand_ratio, 1.5);
            
            return new OmniResult<double>(current_market_price);
        }
    }
}
