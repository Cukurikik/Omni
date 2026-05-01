# OMNI Engine — TOTP Authenticator (Ruby)
# Layer: Security
# Implements: Time-based One-Time Password validation bounds

class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end

  def self.ok(value)
    new(value: value)
  end

  def self.fail(error)
    new(error: error)
  end
end

class TOTPAuthenticator
  def validate_format(code)
    return OmniResult.fail("Code is nil") if code.nil?
    
    code_str = code.to_s
    if code_str.length != 6 || !code_str.match?(/^\d{6}$/)
      return OmniResult.fail("TOTP must be exactly 6 digits")
    end
    
    OmniResult.ok(code_str)
  end

  def check_time_drift(client_timestamp, server_timestamp, allowed_drift_seconds = 30)
    diff = (client_timestamp - server_timestamp).abs
    if diff > allowed_drift_seconds
      return OmniResult.fail("Timestamp drift too large (diff: #{diff}s)")
    end
    
    OmniResult.ok(true)
  end
end
