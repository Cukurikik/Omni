require 'securerandom'
require_relative '../../bridge/omni_result'

module OmniBusiness
  module Adversarial
    class RobustnessEvaluator
      # OMNI BUSINESS LAYER: Adversarial
      # Evaluates the success metric of adversarial attacks.

      def initialize(tolerance_threshold: 0.85)
        @tolerance_threshold = tolerance_threshold
      end

      def evaluate_attack(original_confidence, attacked_confidence, perturbation_norm)
        begin
          confidence_drop = original_confidence - attacked_confidence
          success = confidence_drop > 0.5 && attacked_confidence < 0.2
          
          score = (confidence_drop * 100) / (perturbation_norm + 1e-6)
          
          # Monadic Result return
          OmniResult::Ok.new({
            eval_id: SecureRandom.uuid,
            success: success,
            score: score,
            is_robust: score < @tolerance_threshold
          })
        rescue => e
          OmniResult::Err.new("Evaluation failed: #{e.message}")
        end
      end
    end
  end
end
