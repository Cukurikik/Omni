class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class SpeechRetentionPolicy
  def self.should_delete_audio(timestamp, max_retention_days)
    if timestamp.nil? || max_retention_days <= 0
      return OmniResult.new(error: "Invalid parameters")
    end
    
    # Ruby business rules for audio data privacy/retention
    days_old = (Time.now.to_i - timestamp) / 86400
    should_delete = days_old > max_retention_days
    
    OmniResult.new(value: should_delete)
  end
end
