# OMNI GENERATIVE-MODELS: Classifier-Free Guidance (CFG) Scheduler
# Ruby DSL for scheduling CFG weights over diffusion timesteps to balance quality and fidelity.
# Source: Stability-AI/generative-models

module Omni
  module GenerativeModels
    class CFGSchedulerError < StandardError; end

    class CFGScheduler
      attr_reader :schedule_type

      def initialize(base_cfg = 7.5, schedule_type = :constant)
        @base_cfg = base_cfg
        @schedule_type = schedule_type
      end

      # Returns the CFG scale for a specific timestep.
      # t ranges from 1.0 (start of generation) down to 0.0 (end of generation)
      def get_scale(t)
        raise CFGSchedulerError, "t must be between 0 and 1" if t < 0.0 || t > 1.0

        case @schedule_type
        when :constant
          @base_cfg
        when :linear_decay
          # Start high, decay to 1.0 at the end
          1.0 + (@base_cfg - 1.0) * t
        when :cosine
          # Smooth curve
          1.0 + (@base_cfg - 1.0) * (0.5 * (1.0 - Math.cos(t * Math::PI)))
        else
          raise CFGSchedulerError, "Unknown schedule type"
        end
      end

      # Simulates the actual guidance application
      # result = uncond + cfg * (cond - uncond)
      def apply_guidance(uncond_tensor, cond_tensor, t)
        scale = get_scale(t)
        
        # Simplified vector math simulation
        if uncond_tensor.length != cond_tensor.length
           raise CFGSchedulerError, "Tensor size mismatch"
        end

        result = []
        uncond_tensor.each_with_index do |u, i|
          c = cond_tensor[i]
          result << u + scale * (c - u)
        end
        
        result
      end
    end
  end
end
