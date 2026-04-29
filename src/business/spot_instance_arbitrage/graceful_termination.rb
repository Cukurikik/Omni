module Omni
  module Business
    module SpotInstanceArbitrage
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

      class GracefulTermination
        def handle_termination_notice(seconds_remaining)
          if seconds_remaining < 0
            return OmniResult.new(error: StandardError.new("Time cannot be negative"))
          end

          # Spot Instance Business Logic: Termination Handling
          # AWS gives a 2-minute (120s) warning before killing a spot instance.
          # We must gracefully checkpoint state and drain connections.
          
          if seconds_remaining <= 120
             return OmniResult.new(value: { 
               action: "TRIGGER_CHECKPOINT_AND_DRAIN", 
               reason: "Termination imminent. Entering graceful shutdown sequence." 
             })
          end
          
          OmniResult.new(value: { action: "CONTINUE_NORMAL_OPERATION", reason: "No termination notice." })
        end
      end
    end
  end
end
