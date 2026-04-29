module Omni
  module Semester13
    module Batch08
      class PhysicsRulesetError < StandardError; end

      class Result
        attr_reader :value, :error

        def initialize(value: nil, error: nil)
          @value = value
          @error = error
        end

        def ok?
          @error.nil?
        end

        def unwrap
          raise @error unless ok?
          @value
        end
      end

      # OMNI Engine: physics-rules-ruby
      # Abstract simulation bounds checking against business logical reality.
      class PhysicsRulesetEngine
        def initialize(max_velocity_limit: 300.0)
          @max_velocity = max_velocity_limit
        end

        def evaluate_simulation_viability(velocity_magnitude, kinetic_energy_diff)
          begin
            if velocity_magnitude < 0.0
              return Result.new(error: PhysicsRulesetError.new("Velocity magnitude logically inverted"))
            end

            violation = false
            violation = true if velocity_magnitude > @max_velocity
            violation = true if kinetic_energy_diff > 1.0 # Impossible energy creation

            Result.new(value: { valid_physics: !violation, requires_reset: velocity_magnitude > (@max_velocity * 2) })
          rescue => e
            Result.new(error: PhysicsRulesetError.new("Ruleset fault: #{e.message}"))
          end
        end
      end
    end
  end
end
