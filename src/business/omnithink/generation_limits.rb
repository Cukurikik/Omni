class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class GenerationLimits
  def self.check_token_limit(current_tokens, max_tokens)
    if current_tokens < 0 || max_tokens < 0
      return OmniResult.new(error: "Negative tokens")
    end
    
    # Ruby business logic for capping long-form generation in OmniThink
    can_generate = current_tokens < max_tokens
    
    OmniResult.new(value: can_generate)
  end
end
