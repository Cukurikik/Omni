class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class HardwareLimits
  def self.check_tflops_budget(requested, limit)
    if requested < 0 || limit <= 0
      return OmniResult.new(error: "Invalid TFLOPS parameters")
    end
    
    # Ruby business rules enforcing hardware bounds for CUDA-L2
    is_safe = requested <= limit
    
    OmniResult.new(value: is_safe)
  end
end
