import torch
from torch.optim.optimizer import Optimizer

class OmniAdan(Optimizer):
    """
    Adan: Adaptive Nesterov Momentum Algorithm for Faster Optimizing Deep Models.
    Adapted for OMNI Framework MoE architectures. Ensures efficient gradient updates.
    Based on sail-sg/Adan.
    """
    def __init__(self, params, lr=1e-3, betas=(0.02, 0.08, 0.01), eps=1e-8, weight_decay=0.0):
        if not 0.0 <= lr:
            raise ValueError(f"Invalid learning rate: {lr}")
        if not 0.0 <= eps:
            raise ValueError(f"Invalid epsilon value: {eps}")
        if not 0.0 <= betas[0] < 1.0:
            raise ValueError(f"Invalid beta parameter at index 0: {betas[0]}")
        if not 0.0 <= betas[1] < 1.0:
            raise ValueError(f"Invalid beta parameter at index 1: {betas[1]}")
        if not 0.0 <= betas[2] < 1.0:
            raise ValueError(f"Invalid beta parameter at index 2: {betas[2]}")

        defaults = dict(lr=lr, betas=betas, eps=eps, weight_decay=weight_decay)
        super(OmniAdan, self).__init__(params, defaults)

    @torch.no_grad()
    def step(self, closure=None):
        loss = None
        if closure is not None:
            with torch.enable_grad():
                loss = closure()

        for group in self.param_groups:
            beta1, beta2, beta3 = group['betas']
            lr = group['lr']
            weight_decay = group['weight_decay']
            eps = group['eps']

            for p in group['params']:
                if p.grad is None:
                    continue

                grad = p.grad
                state = self.state[p]

                if len(state) == 0:
                    state['step'] = 0
                    state['exp_avg'] = torch.zeros_like(p, memory_format=torch.preserve_format)
                    state['exp_avg_diff'] = torch.zeros_like(p, memory_format=torch.preserve_format)
                    state['exp_avg_sq'] = torch.zeros_like(p, memory_format=torch.preserve_format)
                    state['pre_grad'] = grad.clone()

                exp_avg, exp_avg_diff, exp_avg_sq = state['exp_avg'], state['exp_avg_diff'], state['exp_avg_sq']
                pre_grad = state['pre_grad']
                state['step'] += 1

                # Calculate gradient difference
                grad_diff = grad - pre_grad

                # Update moving averages
                exp_avg.mul_(1 - beta1).add_(grad, alpha=beta1)
                exp_avg_diff.mul_(1 - beta2).add_(grad_diff, alpha=beta2)
                
                # Estimate variance
                update = grad + beta2 * grad_diff
                exp_avg_sq.mul_(1 - beta3).addcmul_(update, update, value=beta3)

                # Bias corrections
                bias_correction1 = 1 - (1 - beta1) ** state['step']
                bias_correction2 = 1 - (1 - beta2) ** state['step']
                bias_correction3 = 1 - (1 - beta3) ** state['step']

                denom = (exp_avg_sq.sqrt() / math.sqrt(bias_correction3)).add_(eps)

                # Compute step size
                step_size = lr / denom

                # Apply weight decay
                if weight_decay != 0:
                    p.mul_(1 - lr * weight_decay)

                # Nesterov momentum update
                p.addcdiv_(exp_avg, denom, value=-lr)
                p.addcdiv_(exp_avg_diff, denom, value=-lr * beta2)

                pre_grad.copy_(grad)

        return loss

import math
