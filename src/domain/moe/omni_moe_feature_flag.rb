module Omni
  module Domain
    module MoE
      # OMNI MOTHER Production Zero-Mock Feature Flag System
      # Allows dynamic enablement of new MoE models (like VibeBlade or Math Experts)
      # without redeploying the Ruby monolith.

      class FeatureFlagRegistry
        def initialize
          @flags = {}
          @mutex = Mutex.new
        end

        def set_flag(flag_name, is_enabled, percentage_rollout = 100)
          @mutex.synchronize do
            @flags[flag_name.to_s] = {
              enabled: is_enabled,
              rollout: percentage_rollout.clamp(0, 100)
            }
          end
        end

        def enabled?(flag_name, entity_id = nil)
          @mutex.synchronize do
            flag = @flags[flag_name.to_s]
            return false unless flag && flag[:enabled]

            if flag[:rollout] < 100 && entity_id
              # Consistent hashing based on entity ID to determine if they fall in rollout bucket
              hash = Digest::MD5.hexdigest(entity_id.to_s)[0..7].to_i(16)
              bucket = hash % 100
              return bucket < flag[:rollout]
            end

            true
          end
        end

        def all_flags
          @mutex.synchronize { @flags.dup }
        end
      end
    end
  end
end
