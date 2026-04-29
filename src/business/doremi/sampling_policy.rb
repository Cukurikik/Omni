class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class SamplingPolicy
  def self.constrain_weights(calculated_weight)
    if calculated_weight.nil?
      return OmniResult.new(error: "Empty weight")
    end
    
    # Ruby business logic enforcing minimum bounds on domain mixture weights (DoReMi smoothing)
    constrained = calculated_weight < 0.01 ? 0.01 : calculated_weight
    
    OmniResult.new(value: constrained)
  end
end
