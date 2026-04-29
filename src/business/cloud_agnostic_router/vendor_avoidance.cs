using System;

namespace Omni.Business.CloudAgnosticRouter
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class VendorAvoidance
    {
        public OmniResult<string> RouteRequest(bool aws_is_down, bool gcp_is_down, double aws_cost_per_gb, double gcp_cost_per_gb)
        {
            // Multi-Cloud Business Logic: Vendor Lock-In Avoidance & Arbitrage
            // Dynamically shifts traffic away from failing or overpriced cloud providers
            
            if (aws_is_down && gcp_is_down)
            {
                return new OmniResult<string>(new Exception("CRITICAL: All cloud providers unreachable. Falling back to On-Premise."));
            }
            
            if (aws_is_down) return new OmniResult<string>("GCP");
            if (gcp_is_down) return new OmniResult<string>("AWS");
            
            // If both are up, route to the cheaper provider (Cloud Arbitrage)
            if (aws_cost_per_gb < gcp_cost_per_gb)
            {
                return new OmniResult<string>("AWS");
            }
            else
            {
                return new OmniResult<string>("GCP");
            }
        }
    }
}
