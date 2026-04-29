# Omni LLM Agent Benchmark Router (Ruby)
# Business Layer: Routing agent evaluations to correct benchmark suites.
# Ref: zhangxjohn/LLM-Agent-Benchmark-List

module Omni
  module AgentBenchmark
    SUITES = {
      'webshop' => { type: :e2e, max_steps: 50 },
      'alfworld' => { type: :embodied, max_steps: 30 },
      'hotpotqa' => { type: :qa, max_steps: 10 },
      'sciworld' => { type: :science, max_steps: 40 }
    }.freeze

    def self.route(agent_name, suite_name)
      suite = SUITES[suite_name]
      return { error: "Unknown suite: #{suite_name}" } unless suite
      {
        agent: agent_name,
        suite: suite_name,
        type: suite[:type],
        max_steps: suite[:max_steps],
        status: :routed
      }
    end

    def self.compute_success_rate(successes, total)
      return 0.0 if total <= 0
      (successes.to_f / total).round(6)
    end
  end
end
