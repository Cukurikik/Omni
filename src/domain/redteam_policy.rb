# OMNI Domain Layer - Red Team Policy
module Omni
  module Domain
    module RedTeam
      class PolicyError < StandardError; end

      class Result
        attr_reader :value, :error
        
        def initialize(value: nil, error: nil)
          @value = value
          @error = error
        end
        
        def ok?
          @error.nil?
        end
      end

      class ThreatAnalyzer
        def analyze_severity(threat_score, threshold)
          if threat_score < 0 || threshold < 0
            Result.new(error: PolicyError.new("Invalid scoring parameters"))
          elsif threat_score > threshold
            Result.new(value: :critical)
          else
            Result.new(value: :safe)
          end
        end
      end
    end
  end
end
