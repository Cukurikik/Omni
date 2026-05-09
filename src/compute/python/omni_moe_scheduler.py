import math
from torch.optim.lr_scheduler import LRScheduler

# OMNI MOTHER: MoE specific LR Scheduler
# MoE models often require longer warmup and different decay curves.

class OmniMoEScheduler(LRScheduler):
    def __init__(self, optimizer, warmup_steps, total_steps, min_lr_ratio=0.1, last_epoch=-1):
        self.warmup_steps = warmup_steps
        self.total_steps = total_steps
        self.min_lr_ratio = min_lr_ratio
        super().__init__(optimizer, last_epoch)

    def get_lr(self):
        step = self.last_epoch
        if step < self.warmup_steps:
            # Linear warmup
            pct = step / max(1, self.warmup_steps)
            return [base_lr * pct for base_lr in self.base_lrs]
        else:
            # Cosine decay
            progress = (step - self.warmup_steps) / max(1, self.total_steps - self.warmup_steps)
            progress = min(1.0, max(0.0, progress))
            cosine_decay = 0.5 * (1 + math.cos(math.pi * progress))
            decay_factor = self.min_lr_ratio + (1 - self.min_lr_ratio) * cosine_decay
            return [base_lr * decay_factor for base_lr in self.base_lrs]
