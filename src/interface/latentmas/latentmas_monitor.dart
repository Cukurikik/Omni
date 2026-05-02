// @omni-domain Interface Layer (LatentMAS)
// @omni-source various/latentmas
// @omni-description LatentMAS Monitor mimicking Dart/Flutter agent monitoring UI.
// @omni-requirement zero-mock, monadic-error

class OmniResult<T> {
  final bool ok;
  final T? value;
  final Exception? error;

  OmniResult.ok(this.value) : ok = true, error = null;
  OmniResult.err(this.error) : ok = false, value = null;
}

class AgentStatus {
  final String agentId;
  final String status;
  final double cpuUsage;

  AgentStatus(this.agentId, this.status, this.cpuUsage);
}

class LatentMasMonitor {
  final List<AgentStatus> _activeAgents = [];

  OmniResult<bool> updateAgentStatus(String id, String status, double cpu) {
    if (id.isEmpty) {
      return OmniResult.err(Exception("Agent ID cannot be empty"));
    }
    
    _activeAgents.removeWhere((a) => a.agentId == id);
    _activeAgents.add(AgentStatus(id, status, cpu));
    
    return OmniResult.ok(true);
  }

  OmniResult<List<AgentStatus>> getDashboardData() {
    return OmniResult.ok(List.unmodifiable(_activeAgents));
  }
}
