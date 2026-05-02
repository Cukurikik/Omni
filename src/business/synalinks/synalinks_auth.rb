# @omni-domain Business Layer (Synalinks Auth)
class OmniResult
  attr_reader :data, :error
  def initialize(data: nil, error: nil) @data=data; @error=error end
  def self.ok(d) new(data: d) end
  def self.err(e) new(error: e) end
  def ok?() @error.nil? end
end

class SynalinksAuth
  def initialize
    @users = {}
    @tokens = {}
  end
  def register(username, password_hash)
    return OmniResult.err("Username required.") if username.nil? || username.empty?
    return OmniResult.err("Already registered.") if @users.key?(username)
    @users[username] = {password_hash: password_hash, created_at: Time.now.to_s}
    OmniResult.ok(true)
  end
  def authenticate(username, password_hash)
    return OmniResult.err("User not found.") unless @users.key?(username)
    return OmniResult.err("Invalid credentials.") unless @users[username][:password_hash] == password_hash
    token = "tok_#{username}_#{rand(100000)}"
    @tokens[token] = username
    OmniResult.ok({token: token})
  end
  def validate_token(token)
    return OmniResult.err("Invalid token.") unless @tokens.key?(token)
    OmniResult.ok({username: @tokens[token]})
  end
end
