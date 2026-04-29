# Sophia Optimizer — PyTorch Implementation
import torch, math
from typing import Optional, Generic, TypeVar
T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class SophiaG(torch.optim.Optimizer):
    def __init__(self, params, lr=1e-4, betas=(0.965, 0.99), rho=0.04, weight_decay=0.1):
        if lr <= 0: raise ValueError("LR must be positive")
        if rho <= 0: raise ValueError("Rho must be positive")
        defaults = dict(lr=lr, betas=betas, rho=rho, weight_decay=weight_decay)
        super().__init__(params, defaults)

    @torch.no_grad()
    def step(self, closure=None) -> OmniResult[float, str]:
        loss = None
        if closure is not None:
            with torch.enable_grad(): loss = closure()
        for group in self.param_groups:
            lr, wd = group['lr'], group['weight_decay']
            beta1, beta2 = group['betas']
            rho = group['rho']
            for p in group['params']:
                if p.grad is None: continue
                if p.grad.is_sparse: return OmniResult(error="Sparse gradients not supported")
                state = self.state[p]
                if len(state) == 0:
                    state['step'] = 0
                    state['exp_avg'] = torch.zeros_like(p)
                    state['hessian'] = torch.zeros_like(p)
                state['step'] += 1
                exp_avg, hessian = state['exp_avg'], state['hessian']
                # EMA of gradient (momentum)
                exp_avg.mul_(beta1).add_(p.grad, alpha=1 - beta1)
                # Weight decay
                if wd > 0: p.mul_(1 - lr * wd)
                # Sophia update: clip(m_t / max(h_t, rho), 1)
                ratio = exp_avg / hessian.clamp(min=rho)
                update = ratio.clamp(-1.0, 1.0)
                p.add_(update, alpha=-lr)
        return OmniResult(value=loss if loss else 0.0)

    @torch.no_grad()
    def update_hessian(self) -> OmniResult[bool, str]:
        for group in self.param_groups:
            beta2 = group['betas'][1]
            for p in group['params']:
                if p.grad is None: continue
                state = self.state[p]
                if 'hessian' not in state: return OmniResult(error="Must call step() before update_hessian()")
                state['hessian'].mul_(beta2).addcmul_(p.grad, p.grad, value=1 - beta2)
        return OmniResult(value=True)
