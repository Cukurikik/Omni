module OptunaSearch

export OmniResult, compute_expected_improvement

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

# TPE (Tree-structured Parzen Estimator) Math Kernel
function compute_expected_improvement(l_pdf::Vector{Float64}, g_pdf::Vector{Float64}) :: OmniResult{Vector{Float64}, String}
    if length(l_pdf) != length(g_pdf)
        return OmniResult("Lengths of l_pdf and g_pdf must match", Vector{Float64})
    end
    
    if length(l_pdf) == 0
        return OmniResult("PDF vectors cannot be empty", Vector{Float64})
    end

    # Calculate deterministic expected improvement ratio l(x)/g(x)
    ei_scores = zeros(Float64, length(l_pdf))
    
    for i in 1:length(l_pdf)
        if g_pdf[i] < 1e-12
            ei_scores[i] = l_pdf[i] / 1e-12 # Prevent div by zero
        else
            ei_scores[i] = l_pdf[i] / g_pdf[i]
        end
    end

    return OmniResult(ei_scores)
end

end
