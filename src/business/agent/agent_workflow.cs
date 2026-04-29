// OMNI Business Layer: agent_workflow.cs
// C# Domain Logic for orchestrating QuantAgent flows.
// Bound: Max 20 steps per workflow.

using System;
using System.Collections.Generic;

namespace Omni.Semester14.Batch6.Business
{
    public class OmniError
    {
        public int Code { get; set; }
        public string Message { get; set; }
    }

    public class OmniResult<T>
    {
        public T Data { get; set; }
        public OmniError Error { get; set; }
    }

    public class AgentWorkflow
    {
        private const int MAX_WORKFLOW_STEPS = 20;
        private List<string> _steps = new List<string>();

        public OmniResult<bool> AddStep(string stepAction)
        {
            if (_steps.Count >= MAX_WORKFLOW_STEPS)
            {
                return new OmniResult<bool> 
                { 
                    Data = false, 
                    Error = new OmniError { Code = 1, Message = "Workflow exceeds 20 step bound." } 
                };
            }

            _steps.Add(stepAction);
            return new OmniResult<bool> { Data = true, Error = null };
        }

        public int StepCount => _steps.Count;
    }
}
