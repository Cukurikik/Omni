using System;

namespace Omni.Business.SatelliteTelemetryDecoder
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class FaultIsolation
    {
        public OmniResult<string> IsolateSubsystemFault(double battery_voltage, double reaction_wheel_rpm)
        {
            if (battery_voltage < 0 || reaction_wheel_rpm < 0)
            {
                return new OmniResult<string>(new ArgumentException("Telemetry values cannot be negative"));
            }

            // Spacecraft Business Logic: Fault Detection, Isolation, and Recovery (FDIR)
            // If telemetry indicates a critical subsystem failure, the business layer 
            // automatically triggers safe-mode commands.
            
            if (battery_voltage < 22.0)
            {
                return new OmniResult<string>("CRITICAL_FAULT: Power Bus Under-voltage. Entering Safe Mode.");
            }
            
            if (reaction_wheel_rpm > 6000.0)
            {
                return new OmniResult<string>("CRITICAL_FAULT: Reaction Wheel Overspeed. Desaturating instantly.");
            }
            
            return new OmniResult<string>("NOMINAL");
        }
    }
}
