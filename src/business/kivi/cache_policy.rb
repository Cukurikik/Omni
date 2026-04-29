class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class CachePolicy
  def self.determine_quantization_level(available_vram)
    if available_vram < 0
      return OmniResult.new(error: "Invalid VRAM reading")
    end
    
    # Ruby business rules: switch to KIVI 2-bit if VRAM is below threshold
    level = available_vram < 4096 ? "2-bit" : "16-bit"
    
    OmniResult.new(value: level)
  end
end
