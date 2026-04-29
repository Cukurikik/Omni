# Show-o multimodal tier logic
# Ruby business controller

class OmniResult
  attr_reader :is_ok, :value, :error

  def initialize(is_ok, value = nil, error = nil)
    @is_ok = is_ok
    @value = value
    @error = error
  end
end

class ShowOSubscription
  MAX_HD_GENERATIONS_PER_DAY = 50

  def authorize_generation(user_tier, current_usage)
    if user_tier == "free" && current_usage >= 5
      return OmniResult.new(false, nil, "Free tier limit reached")
    end

    if user_tier == "pro" && current_usage >= MAX_HD_GENERATIONS_PER_DAY
      return OmniResult.new(false, nil, "Pro tier daily limit reached")
    end

    OmniResult.new(true, "Authorized")
  end
end
