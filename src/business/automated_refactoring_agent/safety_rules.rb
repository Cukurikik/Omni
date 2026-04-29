module Omni
  module Business
    module AutomatedRefactoringAgent
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

      class RefactorSafetyRules
        def can_apply_refactoring(has_unit_tests, test_coverage_pct, is_public_api)
          if test_coverage_pct < 0.0 || test_coverage_pct > 100.0
            return OmniResult.new(error: StandardError.new("Invalid test coverage percentage"))
          end

          # Refactoring Business Logic: Safety Constraints
          # Prevents the AI agent from breaking production code by ensuring sufficient test coverage exists
          
          if !has_unit_tests
             return OmniResult.new(value: { safe: false, reason: "No unit tests exist to verify behavior" })
          end
          
          if test_coverage_pct < 80.0
             return OmniResult.new(value: { safe: false, reason: "Test coverage below 80% threshold" })
          end
          
          if is_public_api && test_coverage_pct < 95.0
             return OmniResult.new(value: { safe: false, reason: "Public APIs require 95%+ coverage for automated refactoring" })
          end
          
          OmniResult.new(value: { safe: true, reason: "Safety constraints met" })
        end
      end
    end
  end
end
