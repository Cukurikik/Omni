class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class WoodpeckerCorrectionPolicy
  def self.apply_correction(detection_result)
    if detection_result.nil?
      return OmniResult.new(error: "Null detection result")
    end
    
    if detection_result[:hallucinating] && detection_result[:confidence] > 0.8
      # Business rule: Force re-generation if severe hallucination is detected
      OmniResult.new(value: :force_regenerate)
    elsif detection_result[:hallucinating]
      # Soft correction via prompt injection
      OmniResult.new(value: :inject_correction_prompt)
    else
      OmniResult.new(value: :pass)
    end
  end
end
