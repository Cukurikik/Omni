// Omni AutoAgents QA Widget (Dart)
// Ref: AutoLLM/AutoAgents — MIT
class AgentStep { final int step; final String question; final String tool; final String status;
  AgentStep({required this.step, required this.question, required this.tool, required this.status}); }
class OmniAutoAgentsWidget {
  static List<String> decompose(String q) {
    List<String> parts = [q];
    for (var c in [' and ', ' or ']) { List<String> np = []; for (var p in parts) np.addAll(p.split(c)); parts = np; }
    return parts.where((p) => p.trim().isNotEmpty).map((p) => p.trim()).toList();
  }
}
