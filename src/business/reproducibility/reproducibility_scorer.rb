require_relative '../../bridge/omni_result'

module OmniBusiness
  module Reproducibility
    class ReproducibilityScorer
      # OMNI BUSINESS LAYER: Code Reproducibility
      # Calculates a standardized score based on the NeurIPS code release guidelines.

      def initialize(repo_analysis_results)
        @results = repo_analysis_results
      end

      def calculate_score
        begin
          score = 100
          deductions = []

          if @results["has_requirements"].nil? || !@results["has_requirements"]
            score -= 20
            deductions << "Missing requirements.txt or equivalent"
          end

          if @results["has_readme"].nil? || !@results["has_readme"]
            score -= 20
            deductions << "Missing README.md"
          end

          hardcoded_paths = @results["hardcoded_paths"] || []
          if hardcoded_paths.any?
            penalty = [hardcoded_paths.size * 5, 30].min
            score -= penalty
            deductions << "Found #{hardcoded_paths.size} hardcoded absolute paths (-#{penalty} pts)"
          end

          if @results["has_pretrained_weights"].nil? || !@results["has_pretrained_weights"]
            score -= 10
            deductions << "No instructions/links for pretrained weights"
          end

          final_score = [score, 0].max

          OmniResult::Ok.new({
            score: final_score,
            grade: grade_from_score(final_score),
            deductions: deductions
          })
        rescue => e
          OmniResult::Err.new("Score calculation failed: #{e.message}")
        end
      end

      private

      def grade_from_score(score)
        case score
        when 90..100 then "A"
        when 75..89  then "B"
        when 60..74  then "C"
        else "F"
        end
      end
    end
  end
end
