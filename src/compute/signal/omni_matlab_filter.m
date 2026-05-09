% Omni Signal Filter (MATLAB)
% Compute & Signal Processing Layer
% Pre-processes raw time-series data using a Butterworth filter before 
% passing it to the Omni TimeSformer model.

function filtered_signal = omni_butterworth_filter(raw_data, fs, cutoff_freq)
    % raw_data: 1D array of input signals
    % fs: Sampling frequency (Hz)
    % cutoff_freq: Cutoff frequency (Hz)
    
    % Ensure input is a numeric array
    if ~isnumeric(raw_data)
        error('Input raw_data must be numeric.');
    end
    
    % Normalized cutoff frequency (Nyquist)
    Wn = cutoff_freq / (fs / 2);
    
    % Filter order
    n = 4;
    
    % Design the Butterworth low-pass filter
    [b, a] = butter(n, Wn, 'low');
    
    % Apply zero-phase digital filtering to avoid phase distortion
    filtered_signal = filtfilt(b, a, raw_data);
    
    disp('Omni MATLAB: Signal filtering complete.');
end

% Example usage (Simulated execution)
% fs = 1000; % 1 kHz
% t = 0:1/fs:1-1/fs;
% clean_signal = sin(2*pi*50*t);
% noise = 0.5 * randn(size(t));
% raw_signal = clean_signal + noise;
% filtered = omni_butterworth_filter(raw_signal, fs, 100);
