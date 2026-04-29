class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class SimulationLimits
  def self.verify_max_agents(requested_agents, env_capacity)
    if requested_agents < 0 || env_capacity <= 0
      return OmniResult.new(error: "Invalid agent or capacity values")
    end
    
    # Ruby business rules for environment simulation capacity
    is_valid = requested_agents <= env_capacity
    
    OmniResult.new(value: is_valid)
  end
end
