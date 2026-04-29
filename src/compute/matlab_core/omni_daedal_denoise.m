% Omni DAEDAL Matrix Denoiser (MATLAB)
% Compute Layer: Matrix-level variable-length denoising for diffusion LLMs.
% Ref: Li-Jinsong/DAEDAL — ICLR 2026

function result = omni_daedal_denoise(noisy_matrix, noise_scale)
    [rows, cols] = size(noisy_matrix);
    if rows == 0 || cols == 0
        error('OMNI_ERR: Empty matrix');
    end
    correction = noise_scale * exp(-abs(noisy_matrix) * 0.5);
    result = noisy_matrix - correction;
end
