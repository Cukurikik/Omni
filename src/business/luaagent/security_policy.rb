class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class LuaSecurityPolicy
  def self.validate_syscall(syscall_name)
    if syscall_name.nil? || syscall_name.empty?
      return OmniResult.new(error: "Syscall name required")
    end
    
    blocked_syscalls = ["execve", "ptrace", "fork"]
    
    if blocked_syscalls.include?(syscall_name.downcase)
      return OmniResult.new(value: false, error: "Security violation: Blocked syscall")
    end
    
    OmniResult.new(value: true)
  end
end
