using System;
using System.Collections.Generic;

namespace Omni.Business.Swarms {
    public class AgentSwarm {
        public Guid SwarmId { get; private set; }
        private List<string> _agents;

        public AgentSwarm(Guid id) {
            SwarmId = id;
            _agents = new List<string>();
        }

        public void EnrollAgent(string agentId) {
            if (!_agents.Contains(agentId)) {
                _agents.Add(agentId);
            }
        }

        public int GetActiveCount() => _agents.Count;
    }
}
