using System;
using System.Collections.Generic;

namespace Omni.Business.MultiAgentRouter
{
    public class OmniResult<T>
    {
        public T Value { get; }
        public Exception Error { get; }
        public bool IsOk => Error == null;

        public OmniResult(T value) { Value = value; Error = null; }
        public OmniResult(Exception error) { Error = error; }
    }

    public class AgentRegistry
    {
        private readonly HashSet<string> _registeredAgents = new HashSet<string>();

        public OmniResult<bool> RegisterAgent(string agentId, string agentDomain)
        {
            if (string.IsNullOrEmpty(agentId) || string.IsNullOrEmpty(agentDomain))
            {
                return new OmniResult<bool>(new ArgumentException("Agent ID and Domain must be provided"));
            }

            // Multi-Agent Business Logic: Registry Enforcement
            // Ensures no rogue or duplicate agents enter the swarm network
            
            if (_registeredAgents.Contains(agentId))
            {
                return new OmniResult<bool>(new InvalidOperationException("Agent ID already registered to swarm"));
            }

            _registeredAgents.Add(agentId);
            return new OmniResult<bool>(true);
        }
        
        public OmniResult<bool> IsAgentAuthorized(string agentId)
        {
             return new OmniResult<bool>(_registeredAgents.Contains(agentId));
        }
    }
}
