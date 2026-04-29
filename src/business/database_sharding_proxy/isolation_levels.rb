module Omni
  module Business
    module DatabaseShardingProxy
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

      class IsolationLevels
        def validate_cross_shard_transaction(isolation_level)
          if isolation_level.nil? || isolation_level.empty?
            return OmniResult.new(error: StandardError.new("Isolation level must be specified"))
          end

          # Database Business Logic: Transaction Isolation
          # Cross-shard transactions (Two-Phase Commit / Distributed Saga) are notoriously slow and prone to deadlocks.
          # Serializable isolation across shards is strictly forbidden in high-throughput OMNI applications.
          
          if isolation_level.upcase == "SERIALIZABLE"
             return OmniResult.new(value: { 
               allowed: false, 
               reason: "SERIALIZABLE isolation across multiple shards violates performance SLAs. Use READ_COMMITTED and Saga Pattern." 
             })
          end
          
          OmniResult.new(value: { allowed: true, reason: "Isolation level accepted." })
        end
      end
    end
  end
end
