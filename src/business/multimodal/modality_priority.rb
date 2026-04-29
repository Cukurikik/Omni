class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class ModalityPriority
  def self.determine_priority(vision_load, text_load)
    if vision_load < 0 || text_load < 0
      return OmniResult.new(error: "Invalid load metrics")
    end
    
    # Ruby logic deciding bandwidth allocation priority between vision and text
    priority = vision_load > text_load ? "Vision Priority" : "Text Priority"
    
    OmniResult.new(value: priority)
  end
end
