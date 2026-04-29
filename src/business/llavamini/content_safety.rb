class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class ContentSafetyModule
  def self.analyze_content(text)
    if text.nil? || text.empty?
      return OmniResult.new(error: "Empty content")
    end
    
    # Ruby business logic for content safety moderation
    is_safe = !text.include?("violence")
    
    OmniResult.new(value: is_safe)
  end
end
