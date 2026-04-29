% Omni RS SpatioTemporal Matrix Operations (MATLAB)
% High-performance matrix computations for remote sensing VLMs.

function [mean_tensor, err] = omni_compute_spatial_mean(tensor_data)
    % Monadic-style error handling in MATLAB
    err = '';
    mean_tensor = [];

    if isempty(tensor_data)
        err = 'Input tensor data is empty';
        return;
    end

    if ndims(tensor_data) ~= 3
        err = 'Tensor data must be 3-dimensional (Time, X, Y)';
        return;
    end

    % Deterministic temporal mean
    mean_tensor = squeeze(mean(tensor_data, 1));
end
