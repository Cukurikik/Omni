# Omni Agentic Workflow Service (Ruby)
# Ref: arunpshankar/Agentic-Workflow-Patterns — MIT
module Omni
  module AgenticWorkflow
    Pattern = Struct.new(:name, :steps, keyword_init: true)

    PATTERNS = {
      'chain' => 'Sequential execution of steps',
      'parallel' => 'Concurrent execution of independent tasks',
      'router' => 'Route to appropriate handler based on query',
      'evaluator' => 'Evaluate output against criteria',
      'orchestrator' => 'Coordinate multiple agents',
    }.freeze

    def self.create_workflow(pattern_name, steps)
      raise "Unknown pattern: #{pattern_name}" unless PATTERNS.key?(pattern_name)
      Pattern.new(name: pattern_name, steps: steps)
    end

    def self.execute_chain(steps)
      steps.each_with_index.map do |step, i|
        { step: i + 1, name: step, status: 'completed' }
      end
    end

    def self.route_query(query, routes)
      routes.each do |keyword, handler|
        return { matched: keyword, handler: handler } if query.downcase.include?(keyword)
      end
      { matched: 'default', handler: routes.fetch('default', 'general') }
    end
  end
end
