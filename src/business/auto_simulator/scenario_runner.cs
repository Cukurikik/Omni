using System;
using System.Collections.Generic;

namespace Omni.Business.AutoSimulator
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class ScenarioRunner
    {
        private readonly double _maxSimulationTime;

        public ScenarioRunner(double maxSimulationTime = 3600.0) // 1 hour max
        {
            _maxSimulationTime = maxSimulationTime;
        }

        public OmniResult<string> EvaluateScenario(double timeElapsed, int collisionCount)
        {
            if (timeElapsed < 0 || timeElapsed > _maxSimulationTime)
            {
                return new OmniResult<string>(new ArgumentException("Invalid simulation time elapsed"));
            }

            if (collisionCount > 0)
            {
                return new OmniResult<string>("SCENARIO_FAILED: COLLISION_DETECTED");
            }

            if (timeElapsed > _maxSimulationTime * 0.9)
            {
                return new OmniResult<string>("SCENARIO_WARNING: TIME_LIMIT_APPROACHING");
            }

            return new OmniResult<string>("SCENARIO_RUNNING: OPTIMAL");
        }
    }
}
