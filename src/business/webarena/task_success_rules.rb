class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class TaskSuccessRules
  def self.evaluate_task(expected_url, current_url, required_elements)
    if current_url.nil? || current_url.empty?
      return OmniResult.new(error: "Current URL is invalid")
    end
    
    # Ruby business rules for determining if a WebArena agent completed its task successfully
    success = (expected_url == current_url) && !required_elements.empty?
    
    OmniResult.new(value: success)
  end
end
