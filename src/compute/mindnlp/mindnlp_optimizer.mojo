# @omni-domain Compute Layer (MindNLP Optimizer)
# @omni-source mindspore/mindnlp
# @omni-description MindNLP Optimizer mimicking Adam-W with gradient scaling in Mojo.
# @omni-requirement zero-mock, monadic-error

struct OmniResult[T: AnyType]:
    var data: T
    var error: String
    var is_ok: Bool

fn adamw_step(param: Float64, grad: Float64, m: Float64, v: Float64, lr: Float64, beta1: Float64, beta2: Float64, eps: Float64, weight_decay: Float64, step: Int) -> OmniResult[Float64]:
    if step <= 0:
        return OmniResult[Float64](0.0, "Step must be > 0.", False)
    if lr <= 0:
        return OmniResult[Float64](0.0, "Learning rate must be > 0.", False)

    # Update biased moments
    var new_m = beta1 * m + (1.0 - beta1) * grad
    var new_v = beta2 * v + (1.0 - beta2) * grad * grad

    # Bias correction
    var m_hat = new_m / (1.0 - beta1 ** step)
    var v_hat = new_v / (1.0 - beta2 ** step)

    # AdamW weight decay (decoupled)
    var decayed_param = param * (1.0 - lr * weight_decay)

    # Parameter update
    var updated = decayed_param - lr * m_hat / (v_hat ** 0.5 + eps)

    return OmniResult[Float64](updated, "", True)

fn gradient_scale(grad: Float64, scale_factor: Float64) -> OmniResult[Float64]:
    if scale_factor <= 0:
        return OmniResult[Float64](0.0, "Scale factor must be > 0.", False)
    return OmniResult[Float64](grad / scale_factor, "", True)

fn clip_grad_norm(grads: DynamicVector[Float64], max_norm: Float64) -> OmniResult[Float64]:
    if max_norm <= 0:
        return OmniResult[Float64](0.0, "Max norm must be > 0.", False)
    var total_norm: Float64 = 0.0
    for i in range(len(grads)):
        total_norm += grads[i] * grads[i]
    total_norm = total_norm ** 0.5
    var clip_coef = max_norm / (total_norm + 1e-6)
    if clip_coef < 1.0:
        for i in range(len(grads)):
            grads[i] = grads[i] * clip_coef
    return OmniResult[Float64](total_norm, "", True)
