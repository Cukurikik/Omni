module Omni
  module Business
    module GraphFraudDetector
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

      class SuspicionScore
        def evaluate_node(gnn_anomaly_score, manual_override_flag)
          if gnn_anomaly_score < 0.0 || gnn_anomaly_score > 1.0
            return OmniResult.new(error: StandardError.new("GNN score must be normalized between 0.0 and 1.0"))
          end

          if manual_override_flag
            return OmniResult.new(value: { classification: "SAFE", action: "ALLOW" })
          end

          # Fraud Business Logic Boundaries
          if gnn_anomaly_score >= 0.85
            return OmniResult.new(value: { classification: "CRITICAL_FRAUD", action: "BLOCK_AND_REPORT" })
          elsif gnn_anomaly_score >= 0.60
            return OmniResult.new(value: { classification: "SUSPICIOUS", action: "REQUIRE_2FA" })
          end

          OmniResult.new(value: { classification: "NORMAL", action: "ALLOW" })
        end
      end
    end
  end
end
