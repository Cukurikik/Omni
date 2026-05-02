# @omni-domain Business Layer (AI Bootcamp)
# @omni-source various/ai-bootcamp
# @omni-description AI Bootcamp Billing mimicking subscription management in Ruby.
# @omni-requirement zero-mock, monadic-error
class OmniResult
  attr_reader :data, :error
  def initialize(data: nil, error: nil) @data=data; @error=error end
  def self.ok(data) new(data: data) end
  def self.err(error) new(error: error) end
  def ok?() @error.nil? end
end

class BootcampBillingError < StandardError; end

class AIBootcampBilling
  def initialize
    @subscriptions = {}
    @plans = {"basic" => 29.99, "pro" => 79.99, "enterprise" => 199.99}
  end

  def subscribe(user_id, plan)
    return OmniResult.err(BootcampBillingError.new("User ID required.")) if user_id.nil?
    return OmniResult.err(BootcampBillingError.new("Unknown plan: #{plan}")) unless @plans.key?(plan)
    @subscriptions[user_id] = {plan: plan, amount: @plans[plan], status: "active", created_at: Time.now.to_s}
    OmniResult.ok(@subscriptions[user_id])
  end

  def cancel(user_id)
    return OmniResult.err(BootcampBillingError.new("No subscription.")) unless @subscriptions.key?(user_id)
    @subscriptions[user_id][:status] = "cancelled"
    OmniResult.ok(true)
  end

  def invoice(user_id)
    return OmniResult.err(BootcampBillingError.new("No subscription.")) unless @subscriptions.key?(user_id)
    sub = @subscriptions[user_id]
    OmniResult.ok({user: user_id, amount: sub[:amount], plan: sub[:plan], status: sub[:status]})
  end
end
