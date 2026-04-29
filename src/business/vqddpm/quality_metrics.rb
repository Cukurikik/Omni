class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class QualityMetrics
  def self.check_fid_score(fid_score, threshold)
    if fid_score < 0 || threshold < 0
      return OmniResult.new(error: "Invalid FID values")
    end
    
    # Ruby business logic for deciding if generated image quality is acceptable
    is_acceptable = fid_score <= threshold
    
    OmniResult.new(value: is_acceptable)
  end
end
