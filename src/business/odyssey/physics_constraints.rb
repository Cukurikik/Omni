class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class PhysicsConstraints
  def self.apply_gravity(object_mass, current_velocity)
    if object_mass <= 0
      return OmniResult.new(error: "Invalid mass")
    end
    
    # Ruby business rules dictating the physics constraints in the Odyssey virtual world
    new_velocity = current_velocity - 9.81
    
    OmniResult.new(value: new_velocity)
  end
end
