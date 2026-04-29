class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class DecoderConstraints
  def self.validate_resolution(width, height)
    if width < 256 || height < 256
      return OmniResult.new(error: "Resolution too low for decoding")
    end
    
    # Ruby business rules to ensure generated frames meet visual quality criteria
    OmniResult.new(value: true)
  end
end
