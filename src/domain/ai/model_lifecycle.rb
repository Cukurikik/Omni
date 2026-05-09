#=============================================================================
# OMNI DOMAIN LAYER — MODEL LIFECYCLE MANAGEMENT (RUBY)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Ruby domain logic dictating how ML models are loaded and 
#              unloaded from GPU memory to prevent OOM errors.
#=============================================================================

require 'omni_bridge/domain'

module Omni
  module Domain
    module AI
      class ModelLifecycle
        
        # OMNI IDIOM: Resource management via event loop
        def self.load_model_to_gpu(model_id)
          Omni::Result.attempt do
            # 1. Check if model is already loaded in Go Registry
            reg_status = Omni::Bridge::EventLoop.call_sync("domain.models.check_status", { id: model_id })
            return { status: "already_loaded" } if reg_status.data["is_loaded"]

            # 2. Check available VRAM via Telemetry
            telemetry = Omni::Bridge::EventLoop.call_sync("system.telemetry.get_vram", {})
            available_mb = telemetry.data["free_mb"]
            required_mb = reg_status.data["required_mb"]

            if available_mb < required_mb
              # Trigger model eviction policy (LRU)
              Omni::Bridge::EventLoop.call_sync("domain.models.evict_lru", { needed_mb: required_mb })
            end

            # 3. Instruct C++ System Layer to mmap the safetensors into VRAM
            load_res = Omni::Bridge::EventLoop.call_sync("system.tensor.load_safetensors", {
              path: "models/#{model_id}.safetensors",
              target: "gpu"
            })
            raise "VRAM Allocation failed" unless load_res.success?

            # 4. Update Go Registry
            Omni::Bridge::EventLoop.call_sync("domain.models.set_loaded", { id: model_id, handle: load_res.data["handle"] })

            { status: "loaded", handle: load_res.data["handle"] }
          end
        end

      end
    end
  end
end
