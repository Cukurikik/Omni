module QuantumKeyDistributor

export OmniResult, compute_bb84_sift

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

# Deterministic calculation of BB84 Quantum Key Distribution Sifting
# Alice sends photons in random bases (+ or X). Bob measures in random bases.
# They compare bases over a public channel and keep the bits where bases matched.
function compute_bb84_sift(alice_bases::Vector{Int}, bob_bases::Vector{Int}, bob_measurements::Vector{Int}) :: OmniResult{Vector{Int}, String}
    if length(alice_bases) != length(bob_bases) || length(bob_bases) != length(bob_measurements)
        return OmniResult("Vectors must be equal length", Vector{Int})
    end
    
    sifted_key = Int[]
    
    # 0 represents '+' basis (rectilinear)
    # 1 represents 'X' basis (diagonal)
    for i in 1:length(alice_bases)
        if alice_bases[i] == bob_bases[i]
            # Bases matched! The measurement is valid and added to the secure key
            push!(sifted_key, bob_measurements[i])
        end
    end
    
    return OmniResult(sifted_key)
end

end
