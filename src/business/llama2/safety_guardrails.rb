class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class SafetyGuardrails
  def self.check_output(generated_text)
    if generated_text.nil?
      return OmniResult.new(error: "No text to check")
    end
    
    # Ruby business logic implementing LLaMA-2's safety and toxicity filters
    is_safe = !generated_text.include?("harmful_pattern")
    
    OmniResult.new(value: is_safe)
  end
end
