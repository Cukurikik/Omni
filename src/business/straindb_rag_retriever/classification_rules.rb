module Omni
  module Business
    module StraindbRagRetriever
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

      class ClassificationRules
        def determine_strain_species(ani_score)
          if ani_score < 0.0 || ani_score > 1.0
            return OmniResult.new(error: StandardError.new("ANI score must be between 0.0 and 1.0"))
          end

          # StrainsDB Business Logic: Genomic Species Boundary
          # Generally, an ANI > 95% indicates the same species
          
          if ani_score >= 0.95
             return OmniResult.new(value: { classification: "SAME_SPECIES", confidence: "HIGH" })
          elsif ani_score >= 0.83
             return OmniResult.new(value: { classification: "SAME_GENUS", confidence: "MEDIUM" })
          else
             return OmniResult.new(value: { classification: "DISTANT_RELATION", confidence: "LOW" })
          end
        end
      end
    end
  end
end
