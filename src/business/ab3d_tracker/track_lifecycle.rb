module Omni
  module Business
    module Ab3dTracker
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

      class TrackLifecycle
        def evaluate_track(age, time_since_update, max_age_threshold)
          if max_age_threshold <= 0
            return OmniResult.new(error: StandardError.new("max_age_threshold must be positive"))
          end

          # AB3DMOT Business Rules
          # If a track hasn't been associated with a detection for X frames, kill it
          if time_since_update >= max_age_threshold
            return OmniResult.new(value: { state: "DEAD", action: "DELETE_TRACK" })
          end

          # If it's a new track with 1 hit, it's tentative
          if age == 1 && time_since_update == 0
            return OmniResult.new(value: { state: "TENTATIVE", action: "KEEP_TRACK" })
          end

          OmniResult.new(value: { state: "CONFIRMED", action: "KEEP_TRACK" })
        end
      end
    end
  end
end
