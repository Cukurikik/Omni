% Omni PokeChamp Matrix Evaluator (MATLAB)
% Compute Layer: Game state evaluation matrix operations.
% Ref: sethkarten/pokechamp — ICML 2025
function score = omni_pokechamp_eval(state_matrix, weights)
    [r, c] = size(state_matrix);
    if r == 0 || c == 0, error('OMNI_ERR: Empty state'); end
    if length(weights) ~= c, error('OMNI_ERR: Weight mismatch'); end
    score = state_matrix * weights';
end
