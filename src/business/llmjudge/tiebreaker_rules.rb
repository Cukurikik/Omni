class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class TiebreakerRules
  def self.resolve_tie(eval_a, eval_b)
    if eval_a.nil? || eval_b.nil?
      return OmniResult.new(error: "Invalid evaluations")
    end
    
    # Ruby business rules for resolving ties in pairwise LLM judging
    # (e.g., favoring shorter, less repetitive responses)
    winner = "Model A"
    
    OmniResult.new(value: winner)
  end
end
