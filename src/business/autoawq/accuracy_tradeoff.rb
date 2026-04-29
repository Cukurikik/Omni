class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class AccuracyTradeoff
  def self.evaluate_threshold(perplexity_drop, max_allowed_drop)
    if perplexity_drop < 0 || max_allowed_drop < 0
      return OmniResult.new(error: "Negative perplexity drop")
    end
    
    # Ruby business rules for determining if AWQ quantization degrades quality too much
    is_acceptable = perplexity_drop <= max_allowed_drop
    
    OmniResult.new(value: is_acceptable)
  end
end
