module Omni
  module Business
    module TestCoveragePredictor
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

      class CoveragePolicies
        def evaluate_merge_request(current_coverage, new_coverage)
          if current_coverage < 0.0 || new_coverage < 0.0
            return OmniResult.new(error: StandardError.new("Coverage cannot be negative"))
          end

          # Test Coverage Business Logic: Strict Enforcement Policies
          # Prevents code from being merged if it decreases overall project test coverage
          
          if new_coverage < current_coverage
             return OmniResult.new(value: { 
               can_merge: false, 
               reason: "Coverage decrease detected. New code must be fully tested." 
             })
          end
          
          OmniResult.new(value: { can_merge: true, reason: "Coverage maintained or improved" })
        end
      end
    end
  end
end
