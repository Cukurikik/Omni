require_relative '../../bridge/omni_result'

module OmniBusiness
  module HyperTuning
    class TrialTracker
      # OMNI BUSINESS LAYER: Hyperparameter Tuning
      # Tracks tuning trials, scores, and early stopping rules.

      def initialize
        @trials = []
        @best_score = -Float::INFINITY
        @best_hyperparams = nil
      end

      def record_trial(hyperparams, score)
        begin
          trial_id = "trial_#{Time.now.to_i}_#{rand(1000)}"
          trial_record = { id: trial_id, params: hyperparams, score: score }
          
          @trials << trial_record

          if score > @best_score
            @best_score = score
            @best_hyperparams = hyperparams
          end

          # Early stopping logic (Patience = 10)
          if @trials.length > 10
            recent_scores = @trials.last(10).map { |t| t[:score] }
            if recent_scores.max <= @best_score * 1.001
              return OmniResult::Ok.new({ action: :stop, best_params: @best_hyperparams })
            end
          end

          OmniResult::Ok.new({ action: :continue, best_score: @best_score })
        rescue => e
          OmniResult::Err.new("Failed to record trial: #{e.message}")
        end
      end
    end
  end
end
