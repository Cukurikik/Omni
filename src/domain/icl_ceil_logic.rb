module Omni
  module IclCeil
    def self.validate_exemplars(exs)
      if exs.empty?
        return { status: 'error', msg: 'Empty' }
      end
      { status: 'ok', data: true }
    end
  end
end
