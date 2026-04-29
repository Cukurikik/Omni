// Omni effGen Mobile (Dart)
// Mobile Layer: Small agent action display for cross-platform.
// Ref: ctrl-gaurav/effGen
class AgentActionResult { final String action; final double confidence; final bool executed;
  AgentActionResult({required this.action, required this.confidence, required this.executed});
  bool get isViable => confidence >= 0.3;
}
class OmniEffGenMobile {
  static AgentActionResult evaluate(String action, double conf) {
    return AgentActionResult(action: action, confidence: conf.clamp(0.0, 1.0), executed: conf >= 0.3);
  }
}
