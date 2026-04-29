module SimpleHTR

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

function is_ok(res::OmniResult)::Bool
    return res.error === nothing
end

function ctc_best_path_decode(log_probs::Matrix{Float64}, blank_index::Int)::OmniResult{Vector{Int}, String}
    time_steps, num_classes = size(log_probs)

    if blank_index < 1 || blank_index > num_classes
        return OmniResult{Vector{Int}, String}(nothing, "Blank index out of bounds")
    end

    # Deterministic mathematical CTC Best Path Decoding
    raw_sequence = Int[]
    for t in 1:time_steps
        max_val = -Inf
        best_idx = -1
        for c in 1:num_classes
            if log_probs[t, c] > max_val
                max_val = log_probs[t, c]
                best_idx = c
            end
        end
        push!(raw_sequence, best_idx)
    end

    # Collapse repeated chars and remove blanks
    decoded = Int[]
    prev_char = -1
    
    for char_idx in raw_sequence
        if char_idx != blank_index && char_idx != prev_char
            push!(decoded, char_idx)
        end
        prev_char = char_idx
    end

    return OmniResult{Vector{Int}, String}(decoded, nothing)
end

end
