# FastEdit ROME Covariance Statistics Collector
# Julia SIMD-optimized covariance matrix computation

module ROMECovariance

struct OmniResult{T, E}
    is_ok::Bool; value::Union{T, Nothing}; error::Union{E, Nothing}
end

const MAX_HIDDEN_DIM = 16384
const MAX_SAMPLES = 1000000

function compute_covariance(activations::Matrix{Float32})::OmniResult{Matrix{Float64}, String}
    n, d = size(activations)
    if d > MAX_HIDDEN_DIM
        return OmniResult{Matrix{Float64}, String}(false, nothing, "Hidden dim exceeds $MAX_HIDDEN_DIM")
    end
    if n > MAX_SAMPLES
        return OmniResult{Matrix{Float64}, String}(false, nothing, "Sample count exceeds $MAX_SAMPLES")
    end
    mean_vec = zeros(Float64, d)
    @simd for j in 1:d
        s = 0.0
        @inbounds for i in 1:n
            s += Float64(activations[i, j])
        end
        mean_vec[j] = s / n
    end
    cov = zeros(Float64, d, d)
    for i in 1:n
        centered = Float64.(activations[i, :]) .- mean_vec
        cov .+= centered * centered'
    end
    cov ./= (n - 1)
    return OmniResult{Matrix{Float64}, String}(true, cov, nothing)
end

end
