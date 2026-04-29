module OmniFFTProcessor

using FFTW

struct FFTError <: Exception
    msg::String
end

function process_signal(signal::Vector{ComplexF64})::Vector{ComplexF64}
    if length(signal) == 0
        throw(FFTError("Empty signal provided"))
    end
    # High performance in-place execution via FFTW
    return fft(signal)
end

function compute_power_spectrum(signal::Vector{ComplexF64})::Vector{Float64}
    transformed = process_signal(signal)
    return abs2.(transformed)
end

end # module
