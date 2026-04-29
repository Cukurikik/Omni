class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class ComputeBudget
  def self.calculate_cost(gpu_hours, cost_per_hour)
    if gpu_hours < 0 || cost_per_hour < 0
      return OmniResult.new(error: "Values cannot be negative")
    end
    
    # Ruby business logic for Megatron-LM cluster cost estimation
    total_cost = gpu_hours * cost_per_hour
    
    OmniResult.new(value: total_cost)
  end
end
