% Omni DeCo Softmax Evaluator (MATLAB)
% Compute Layer: Softmax with dynamic penalty for correction decoding.
% Ref: zjunlp/Deco — ICLR 2025
function probs = omni_deco_softmax(logits, penalty_mask, penalty_val)
    corrected = logits - penalty_mask * penalty_val;
    mx = max(corrected);
    ex = exp(corrected - mx);
    probs = ex / sum(ex);
end
