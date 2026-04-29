class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class ModalityFallback
  def self.determine_fallback(failed_modality)
    if failed_modality.nil?
      return OmniResult.new(error: "No modality specified")
    end
    
    # Ruby business rules: fallback from vision/audio to text if bandwidth drops
    fallback = failed_modality == "vision" ? "text" : "audio"
    
    OmniResult.new(value: fallback)
  end
end
