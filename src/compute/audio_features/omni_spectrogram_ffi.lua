-- omni_spectrogram_ffi.lua — Lua Spectrogram FFI for Audio Processing
-- Inspired by: SoundStorm audio preprocessing pipeline
-- Layer: Compute / Lua Scripting
--
-- LuaJIT FFI bindings for real-time mel-spectrogram extraction
-- used in OMNI's audio codec preprocessing pipeline.

local ffi = require("ffi")
local bit = require("bit")

local M = {}

-- Constants
M.SAMPLE_RATE = 16000
M.N_FFT = 1024
M.HOP_LENGTH = 256
M.N_MELS = 128
M.F_MIN = 0.0
M.F_MAX = 8000.0

-- Hann window
function M.hann_window(n)
    local window = {}
    for i = 0, n - 1 do
        window[i + 1] = 0.5 * (1.0 - math.cos(2.0 * math.pi * i / (n - 1)))
    end
    return window
end

-- Hz to Mel conversion
function M.hz_to_mel(freq)
    return 2595.0 * math.log10(1.0 + freq / 700.0)
end

-- Mel to Hz conversion
function M.mel_to_hz(mel)
    return 700.0 * (10.0 ^ (mel / 2595.0) - 1.0)
end

-- Create mel filterbank
function M.mel_filterbank(n_mels, n_fft, sample_rate, f_min, f_max)
    local n_freqs = math.floor(n_fft / 2) + 1
    local mel_min = M.hz_to_mel(f_min)
    local mel_max = M.hz_to_mel(f_max)

    -- Create mel points
    local mel_points = {}
    for i = 0, n_mels + 1 do
        mel_points[i + 1] = mel_min + (mel_max - mel_min) * i / (n_mels + 1)
    end

    -- Convert to Hz and then to FFT bin indices
    local hz_points = {}
    local bin_points = {}
    for i = 1, #mel_points do
        hz_points[i] = M.mel_to_hz(mel_points[i])
        bin_points[i] = math.floor((n_fft + 1) * hz_points[i] / sample_rate)
    end

    -- Create triangular filters
    local filterbank = {}
    for m = 1, n_mels do
        filterbank[m] = {}
        for k = 1, n_freqs do
            filterbank[m][k] = 0.0
        end

        local f_start = bin_points[m]
        local f_center = bin_points[m + 1]
        local f_end = bin_points[m + 2]

        -- Rising slope
        for k = f_start, f_center do
            if k >= 1 and k <= n_freqs and f_center > f_start then
                filterbank[m][k] = (k - f_start) / (f_center - f_start)
            end
        end

        -- Falling slope
        for k = f_center, f_end do
            if k >= 1 and k <= n_freqs and f_end > f_center then
                filterbank[m][k] = (f_end - k) / (f_end - f_center)
            end
        end
    end

    return filterbank
end

-- Simple DFT (for environments without FFI FFTW)
function M.dft_real(signal, n_fft)
    local n_freqs = math.floor(n_fft / 2) + 1
    local real_part = {}
    local imag_part = {}

    for k = 1, n_freqs do
        real_part[k] = 0.0
        imag_part[k] = 0.0
        local freq = (k - 1)
        for n = 1, n_fft do
            local angle = -2.0 * math.pi * freq * (n - 1) / n_fft
            real_part[k] = real_part[k] + signal[n] * math.cos(angle)
            imag_part[k] = imag_part[k] + signal[n] * math.sin(angle)
        end
    end

    -- Power spectrum
    local power = {}
    for k = 1, n_freqs do
        power[k] = real_part[k] * real_part[k] + imag_part[k] * imag_part[k]
    end

    return power
end

-- STFT with Hann window
function M.stft(audio, n_fft, hop_length)
    local window = M.hann_window(n_fft)
    local num_samples = #audio
    local num_frames = math.floor((num_samples - n_fft) / hop_length) + 1
    local n_freqs = math.floor(n_fft / 2) + 1

    local spectrogram = {}

    for frame = 1, num_frames do
        local start = (frame - 1) * hop_length
        local windowed = {}

        for i = 1, n_fft do
            local idx = start + i
            if idx <= num_samples then
                windowed[i] = audio[idx] * window[i]
            else
                windowed[i] = 0.0
            end
        end

        spectrogram[frame] = M.dft_real(windowed, n_fft)
    end

    return spectrogram, num_frames, n_freqs
end

-- Convert power spectrogram to mel spectrogram
function M.power_to_mel(spectrogram, filterbank, num_frames, n_mels, n_freqs)
    local mel_spec = {}

    for frame = 1, num_frames do
        mel_spec[frame] = {}
        for m = 1, n_mels do
            local energy = 0.0
            for k = 1, n_freqs do
                energy = energy + spectrogram[frame][k] * filterbank[m][k]
            end
            mel_spec[frame][m] = energy
        end
    end

    return mel_spec
end

-- Convert to log-mel spectrogram
function M.log_mel(mel_spec, num_frames, n_mels, ref_level, min_level)
    ref_level = ref_level or 1.0
    min_level = min_level or 1e-10

    local log_spec = {}
    for frame = 1, num_frames do
        log_spec[frame] = {}
        for m = 1, n_mels do
            local val = math.max(mel_spec[frame][m], min_level)
            log_spec[frame][m] = 10.0 * math.log10(val / ref_level)
        end
    end

    return log_spec
end

-- Normalize spectrogram to [0, 1]
function M.normalize(log_spec, num_frames, n_mels)
    local min_val = math.huge
    local max_val = -math.huge

    for f = 1, num_frames do
        for m = 1, n_mels do
            min_val = math.min(min_val, log_spec[f][m])
            max_val = math.max(max_val, log_spec[f][m])
        end
    end

    local range = max_val - min_val
    if range < 1e-10 then range = 1.0 end

    local normalized = {}
    for f = 1, num_frames do
        normalized[f] = {}
        for m = 1, n_mels do
            normalized[f][m] = (log_spec[f][m] - min_val) / range
        end
    end

    return normalized
end

-- Full pipeline: audio waveform -> normalized log-mel spectrogram
function M.extract_features(audio, config)
    config = config or {}
    local n_fft = config.n_fft or M.N_FFT
    local hop = config.hop_length or M.HOP_LENGTH
    local n_mels = config.n_mels or M.N_MELS
    local sr = config.sample_rate or M.SAMPLE_RATE
    local f_min = config.f_min or M.F_MIN
    local f_max = config.f_max or M.F_MAX

    local filterbank = M.mel_filterbank(n_mels, n_fft, sr, f_min, f_max)
    local spec, num_frames, n_freqs = M.stft(audio, n_fft, hop)
    local mel = M.power_to_mel(spec, filterbank, num_frames, n_mels, n_freqs)
    local log = M.log_mel(mel, num_frames, n_mels)
    local normed = M.normalize(log, num_frames, n_mels)

    return normed, num_frames, n_mels
end

return M
