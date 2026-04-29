using System;
using System.Collections.Generic;

namespace Omni.Business.RoboticTeleop
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class SafetyLimits
    {
        private readonly double _maxVelocityRadPerSec;
        private readonly List<double> _jointLimitsMin;
        private readonly List<double> _jointLimitsMax;

        public SafetyLimits()
        {
            _maxVelocityRadPerSec = 2.0;
            // 6 DOF limits
            _jointLimitsMin = new List<double> { -3.14, -1.57, -1.57, -3.14, -1.57, -3.14 };
            _jointLimitsMax = new List<double> { 3.14, 1.57, 1.57, 3.14, 1.57, 3.14 };
        }

        public OmniResult<string> ValidateMovementCommand(List<double> targetJoints, double requestedVelocity)
        {
            if (targetJoints == null || targetJoints.Count != 6)
                return new OmniResult<string>(new ArgumentException("Exactly 6 joint angles required"));

            if (requestedVelocity > _maxVelocityRadPerSec)
                return new OmniResult<string>(new InvalidOperationException($"Velocity {requestedVelocity} exceeds safe limit {_maxVelocityRadPerSec}"));

            for (int i = 0; i < 6; i++)
            {
                if (targetJoints[i] < _jointLimitsMin[i] || targetJoints[i] > _jointLimitsMax[i])
                {
                    return new OmniResult<string>(new InvalidOperationException($"Joint {i} target {targetJoints[i]} is outside physical limits"));
                }
            }

            return new OmniResult<string>("COMMAND_SAFE");
        }
    }
}
