// Compose Agent Manager in C#
using System;
using System.Collections.Generic;

namespace Omni.ComposeForAgents {
    public class OmniResult<T, E> {
        public bool IsOk { get; set; }
        public T Value { get; set; }
        public E Error { get; set; }
    }

    public class AgentManager {
        private Dictionary<string, string> _agents = new Dictionary<string, string>();

        public OmniResult<bool, string> RegisterAgent(string agentId, string type) {
            if (string.IsNullOrEmpty(agentId)) return new OmniResult<bool, string> { IsOk = false, Error = "ID empty" };
            if (_agents.ContainsKey(agentId)) return new OmniResult<bool, string> { IsOk = false, Error = "Agent exists" };
            
            _agents[agentId] = type;
            return new OmniResult<bool, string> { IsOk = true, Value = true };
        }
    }
}
