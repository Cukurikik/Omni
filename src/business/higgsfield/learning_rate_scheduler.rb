module Omni
  module Higgsfield
    # OMNI Higgsfield - Dynamic Learning Rate Scheduler
    # Ruby Domain Logic for calculating LR decay in trillion-parameter training
    
    class LearningRateScheduler
      attr_reader :base_lr, :warmup_steps, :total_steps, :min_lr

      def initialize(base_lr: 1e-4, warmup_steps: 2000, total_steps: 100000, min_lr: 1e-6)
        @base_lr = base_lr
        @warmup_steps = warmup_steps
        @total_steps = total_steps
        @min_lr = min_lr
      end

      # Returns [Boolean (success), Float/String (lr_value or error)]
      def compute_lr(current_step)
        return [false, "Step cannot be negative"] if current_step < 0
        return [true, @min_lr] if current_step >= @total_steps

        if current_step < @warmup_steps
          # Linear warmup
          lr = @min_lr + (@base_lr - @min_lr) * (current_step.to_f / @warmup_steps)
          [true, lr]
        else
          # Cosine decay
          decay_steps = @total_steps - @warmup_steps
          progress = (current_step - @warmup_steps).to_f / decay_steps
          cosine_decay = 0.5 * (1 + Math.cos(Math::PI * progress))
          lr = @min_lr + (@base_lr - @min_lr) * cosine_decay
          [true, lr]
        end
      end
    end
  end
end
