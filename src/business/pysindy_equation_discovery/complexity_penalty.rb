module Omni
  module Business
    module PySindyEquationDiscovery
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

      class ComplexityPenalty
        def evaluate_equation(term_count, max_terms_allowed, accuracy_score)
          if max_terms_allowed <= 0
            return OmniResult.new(error: StandardError.new("max_terms_allowed must be positive"))
          end

          if accuracy_score < 0.0 || accuracy_score > 1.0
            return OmniResult.new(error: StandardError.new("accuracy_score must be bounded between 0.0 and 1.0"))
          end

          # Occam's Razor enforcement for Equation Discovery
          if term_count > max_terms_allowed
            return OmniResult.new(value: { verdict: "REJECTED", reason: "TOO_COMPLEX", action: "INCREASE_SPARSITY_THRESHOLD" })
          end

          if accuracy_score < 0.70
            return OmniResult.new(value: { verdict: "REJECTED", reason: "LOW_ACCURACY", action: "DECREASE_SPARSITY_THRESHOLD" })
          end

          OmniResult.new(value: { verdict: "ACCEPTED", reason: "PARSIMONIOUS_AND_ACCURATE", action: "PUBLISH_EQUATION" })
        end
      end
    end
  end
end
