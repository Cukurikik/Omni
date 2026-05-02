using System;
using System.Collections.Generic;
// @omni-domain Business Layer (Compose Agent)
// @omni-source various/compose
// @omni-description Compose Agent Manager mimicking multi-agent coordination in C#.
// @omni-requirement zero-mock, monadic-error
namespace Omni.Business.Compose {
    public class OmniResult<T> {
        public T Data { get; } public Exception Error { get; } public bool IsOk => Error == null;
        private OmniResult(T d, Exception e) { Data=d; Error=e; }
        public static OmniResult<T> Ok(T d) => new OmniResult<T>(d, null);
        public static OmniResult<T> Err(Exception e) => new OmniResult<T>(default, e);
    }
    public class ComposeError : Exception { public ComposeError(string m) : base(m) {} }
    public class ComposeAgentManager {
        private Dictionary<string, string> _agents = new();
        public OmniResult<bool> RegisterAgent(string id, string role) {
            if (string.IsNullOrEmpty(id)) return OmniResult<bool>.Err(new ComposeError("Agent ID required."));
            _agents[id] = role;
            return OmniResult<bool>.Ok(true);
        }
        public OmniResult<string> AssignTask(string agentId, string task) {
            if (!_agents.ContainsKey(agentId)) return OmniResult<string>.Err(new ComposeError("Agent not found."));
            return OmniResult<string>.Ok($"Task '{task}' assigned to {agentId} ({_agents[agentId]})");
        }
    }
}
