module Omni
  module Semester13
    module Batch07
      class SketchPolicyError < StandardError; end

      class Result
        attr_reader :value, :error

        def initialize(value: nil, error: nil)
          @value = value
          @error = error
        end

        def ok?
          @error.nil?
        end

        def unwrap
          raise @error unless ok?
          @value
        end
      end

      # OMNI Engine: sketch-policy
      # Domain limits for vector simplification and bounding rules.
      class SketchPolicyEngine
        def initialize(min_stroke_length: 5.0)
          @min_stroke_length = min_stroke_length
        end

        def evaluate_stroke_validity(length, complexity_ratio)
          begin
            if length < 0.0 || complexity_ratio < 0.0
              return Result.new(error: SketchPolicyError.new("Geometric bounds strictly positive"))
            end

            is_valid = true
            is_valid = false if length < @min_stroke_length
            is_valid = false if complexity_ratio > 10.0 # overly complex scribble rejection

            Result.new(value: { valid: is_valid, review_required: complexity_ratio > 8.0 })
          rescue => e
            Result.new(error: SketchPolicyError.new("Stroke policy fault: #{e.message}"))
          end
        end

        def validate_reasoning_gap(divergence_rads)
           begin
               if divergence_rads < 0.0
                  return Result.new(error: SketchPolicyError.new("Divergence angle mathematically invalid"))
               end
               
               penalty = [divergence_rads * 100.0, 50.0].min
               Result.new(value: { penalty_points: penalty, is_acceptable: divergence_rads < 0.3 })
           rescue => e
               Result.new(error: SketchPolicyError.new("Gap bounds fault: #{e.message}"))
           end
        end
      end
    end
  end
end
