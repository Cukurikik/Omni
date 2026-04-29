using System;

namespace Omni.Business.IDETelemetryTracker
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class PrivacyRules
    {
        public OmniResult<bool> ShouldScrubTelemetryEvent(string event_payload)
        {
            if (string.IsNullOrEmpty(event_payload))
            {
                return new OmniResult<bool>(new ArgumentException("Payload cannot be empty"));
            }

            // IDE Telemetry Business Logic: Privacy & GDPR scrubbing
            // Never transmit hardcoded secrets, PII, or internal IPs to the telemetry dashboard
            
            bool contains_secret = event_payload.Contains("password") || event_payload.Contains("api_key") || event_payload.Contains("sk-");
            bool contains_ip = event_payload.Contains("192.168.") || event_payload.Contains("10.0.");

            if (contains_secret || contains_ip)
            {
                // Scrub this event before transmission
                return new OmniResult<bool>(true);
            }
            
            return new OmniResult<bool>(false);
        }
    }
}
