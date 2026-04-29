class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class PrivacyFilter
  def self.check_note_export(note_content)
    if note_content.nil?
      return OmniResult.new(error: "Empty content")
    end
    
    # Ruby business rules preventing sensitive notes from being sent to external APIs
    is_safe = !note_content.include?("CONFIDENTIAL")
    
    OmniResult.new(value: is_safe)
  end
end
