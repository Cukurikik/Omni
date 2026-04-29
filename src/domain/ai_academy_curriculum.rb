# OMNI Domain Layer - AI Academy Curriculum
module Omni
  module Domain
    module AIAcademy
      class CurriculumError < StandardError; end

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

      class ProgressionValidator
        def validate_prerequisites(completed_modules, required_module)
          if !completed_modules.include?(required_module)
            Result.new(error: CurriculumError.new("Prerequisite module not completed"))
          else
            Result.new(value: true)
          end
        end
      end
    end
  end
end
