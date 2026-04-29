class OmniResult
  attr_reader :value, :error, :is_ok

  def initialize(value: nil, error: nil)
    @value = value
    @error = error
    @is_ok = error.nil?
  end
end

class SqueezeCompressionPolicy
  def self.determine_sparsity(model_size_mb, target_size_mb)
    if model_size_mb <= 0 || target_size_mb <= 0
      return OmniResult.new(error: "Invalid sizes")
    end
    
    ratio = target_size_mb.to_f / model_size_mb.to_f
    
    # Mathematical policy allocation
    sparsity_threshold = if ratio > 0.8
                           0.01
                         elsif ratio > 0.5
                           0.05
                         else
                           0.1
                         end
               
    OmniResult.new(value: sparsity_threshold)
  end
end
