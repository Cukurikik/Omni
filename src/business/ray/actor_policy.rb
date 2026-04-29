class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class ActorPolicy
  def self.check_liveness(actor_id, last_heartbeat)
    if actor_id.nil?
      return OmniResult.new(error: "Actor ID missing")
    end
    
    # Ruby business rules for Ray actor lifecycle management
    # Dead if no heartbeat for 30 seconds
    is_alive = (Time.now.to_i - last_heartbeat) < 30
    
    OmniResult.new(value: is_alive)
  end
end
