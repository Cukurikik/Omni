module Omni
  module Business
    module HuggingFaceHub
      class OmniResult
        attr_reader :value, :error
        
        def initialize(value: nil, error: nil)
          @value = value
          @error = error
        end
        
        def ok?
          @error.nil?
        end
      end

      class RetentionPolicy
        def initialize(max_cache_gb: 50.0)
          @max_cache_bytes = max_cache_gb * 1024 * 1024 * 1024
        end

        def validate_cache_addition(current_cache_bytes, new_model_bytes)
          if new_model_bytes <= 0
            return OmniResult.new(error: StandardError.new("Model size must be positive"))
          end

          total_bytes = current_cache_bytes + new_model_bytes

          if total_bytes > @max_cache_bytes
            # Business rule: Must trigger LRU eviction
            return OmniResult.new(value: { allowed: true, trigger_eviction: true, overflow: total_bytes - @max_cache_bytes })
          end

          OmniResult.new(value: { allowed: true, trigger_eviction: false, overflow: 0 })
        end
      end
    end
  end
end
