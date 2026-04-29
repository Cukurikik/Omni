module Omni
  module AgentVerse
    def self.apply_rules(rules)
      if rules.empty?
        return { status: 'error', msg: 'No rules' }
      end
      { status: 'ok', data: true }
    end
  end
end
