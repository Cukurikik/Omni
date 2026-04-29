module Omni
  module Business
    module ExoSkeletonActuator
      class OmniResult
        attr_reader :value, :error
        
        def initialize(value: nil, error: nil)
          @value = value
          @error = error
        end
        
        def ok?
          @error.nil?
        end
      end

      class TorqueCutoffs
        def validate_joint_torque(requested_torque_nm, max_human_tolerance_nm)
          if requested_torque_nm < 0 || max_human_tolerance_nm <= 0
            return OmniResult.new(error: StandardError.new("Torque must be positive"))
          end

          # Exoskeleton Business Logic: Human Safety Override
          # If the system attempts to apply a torque that exceeds the structural limits 
          # of human bone/ligaments (e.g., knee joint over-extension), we must kill the servos instantly.
          
          if requested_torque_nm > max_human_tolerance_nm
             return OmniResult.new(value: { 
               safe: false, 
               reason: "EMERGENCY: Requested torque exceeds human biological limits. Actuators disengaged." 
             })
          end
          
          OmniResult.new(value: { safe: true, reason: "Torque within safe operating margins." })
        end
      end
    end
  end
end
