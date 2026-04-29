package dev.omni.batch9;
import java.util.*;

public class LLMAgentSurveyCoordinator {
    private static final int MAX_AGENTS = 100;
    private final Map<String, Map<String, Object>> agents = new HashMap<>();

    public Map<String, Object> registerAgent(String id, String capability) {
        if (id == null || id.isEmpty()) return Map.of("isOk", false, "error", "Missing agent ID");
        if (agents.size() >= MAX_AGENTS) return Map.of("isOk", false, "error", "Agent limit reached");
        agents.put(id, Map.of("capability", capability, "status", "ready"));
        return Map.of("isOk", true, "value", id);
    }

    public Map<String, Object> dispatchTask(String agentId, String task) {
        if (!agents.containsKey(agentId)) return Map.of("isOk", false, "error", "Agent not found");
        if (task == null || task.length() > 65536) return Map.of("isOk", false, "error", "Invalid task");
        return Map.of("isOk", true, "value", Map.of("agent", agentId, "task_len", task.length()));
    }
}
