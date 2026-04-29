module Omni
  module Business
    module EmbeddedRagIndexer
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

      class FlashStorageRules
        def can_write_index(estimated_write_mb, remaining_tbw)
          if estimated_write_mb < 0.0 || remaining_tbw < 0.0
            return OmniResult.new(error: StandardError.new("Invalid storage metrics"))
          end

          # Embedded RAG Business Logic: Flash Storage Endurance
          # Embedded IoT devices (e.g. Raspberry Pi SD cards) have strict Total Bytes Written (TBW) limits
          # Prevent aggressive RAG indexing from destroying the device storage
          
          # Convert MB to TB
          write_tb = estimated_write_mb / (1024.0 * 1024.0)
          
          if write_tb > (remaining_tbw * 0.05)
             # Don't allow a single index operation to burn more than 5% of remaining device lifespan
             return OmniResult.new(value: { 
               allowed: false, 
               reason: "Index too large. Exceeds safe flash storage write-cycle limits." 
             })
          end
          
          OmniResult.new(value: { allowed: true, reason: "Write cycle within safe endurance limits." })
        end
      end
    end
  end
end
