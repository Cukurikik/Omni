module Omni
  module UoT
    def self.decide(entropy)
      if entropy < 0
        return { status: 'error', msg: 'Negative entropy' }
      end
      { status: 'ok', data: 'action_a' }
    end
  end
end
