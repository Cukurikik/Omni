using System;

namespace Omni.Business.IoTSensorFusion
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class CalibrationRules
    {
        public OmniResult<bool> IsSensorCalibrated(double kalman_error_covariance, double max_acceptable_error)
        {
            if (kalman_error_covariance < 0.0 || max_acceptable_error <= 0.0)
            {
                return new OmniResult<bool>(new ArgumentException("Invalid covariance thresholds"));
            }

            // IoT Sensor Business Logic: Calibration Confidence
            // If the fused sensor data is too noisy (high error covariance), 
            // the system should refuse to trigger critical physical actions (e.g., Drone landing)
            
            if (kalman_error_covariance > max_acceptable_error)
            {
                // Sensor is drifting or uncalibrated
                return new OmniResult<bool>(false);
            }
            
            return new OmniResult<bool>(true);
        }
    }
}
