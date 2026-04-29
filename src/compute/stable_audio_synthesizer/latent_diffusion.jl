module StableAudioSynthesizer

export OmniResult, compute_noise_schedule

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
    is_ok::Bool
end

function OmniResult(value::T) where T
    OmniResult{T, String}(value, nothing, true)
end

function OmniResult(error::String, ::Type{T}=Any) where T
    OmniResult{T, String}(nothing, error, false)
end

# Deterministic calculation of Diffusion Noise Schedule (beta schedule)
function compute_noise_schedule(timesteps::Int, beta_start::Float64, beta_end::Float64) :: OmniResult{Vector{Float64}, String}
    if timesteps <= 0
        return OmniResult("Timesteps must be positive", Vector{Float64})
    end
    
    if beta_start >= beta_end
        return OmniResult("beta_start must be less than beta_end", Vector{Float64})
    end

    # Linear noise schedule for Latent Diffusion Models
    betas = Vector{Float64}(undef, timesteps)
    step = (beta_end - beta_start) / (timesteps - 1)
    
    for i in 1:timesteps
        betas[i] = beta_start + step * (i - 1)
    end
    
    return OmniResult(betas)
end

end
