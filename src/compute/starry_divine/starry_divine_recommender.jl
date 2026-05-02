# @omni-domain Compute Layer (Recommender Systems)
# @omni-source various/starry-divine
# @omni-description Starry Divine Recommender mimicking collaborative filtering in Julia.
# @omni-requirement zero-mock, monadic-error

struct OmniResult{T}
    data::Union{T, Nothing}
    error::Union{String, Nothing}
end

OmniResult(data::T) where T = OmniResult{T}(data, nothing)
OmniResult(;error::String) = OmniResult{Nothing}(nothing, error)
is_ok(r::OmniResult) = isnothing(r.error)

function cosine_similarity(a::Vector{Float64}, b::Vector{Float64})
    if length(a) != length(b)
        return 0.0
    end
    dot_prod = sum(a .* b)
    norm_a = sqrt(sum(a .^ 2))
    norm_b = sqrt(sum(b .^ 2))
    return (norm_a > 0 && norm_b > 0) ? dot_prod / (norm_a * norm_b) : 0.0
end

function recommend_items(user_ratings::Dict{String,Vector{Float64}}, target_user::String, top_k::Int=5)
    if !haskey(user_ratings, target_user)
        return OmniResult(error="Target user not found.")
    end
    if isempty(user_ratings) || length(user_ratings) < 2
        return OmniResult(error="Need at least 2 users.")
    end

    target_vec = user_ratings[target_user]
    similarities = Dict{String,Float64}()

    for (user, vec) in user_ratings
        if user != target_user
            similarities[user] = cosine_similarity(target_vec, vec)
        end
    end

    n_items = length(target_vec)
    scores = zeros(Float64, n_items)
    weights = zeros(Float64, n_items)

    for (user, sim) in similarities
        if sim > 0
            vec = user_ratings[user]
            for i in 1:n_items
                if target_vec[i] == 0.0 && vec[i] > 0
                    scores[i] += sim * vec[i]
                    weights[i] += sim
                end
            end
        end
    end

    recommendations = []
    for i in 1:n_items
        if target_vec[i] == 0.0 && weights[i] > 0
            push!(recommendations, (item=i, score=scores[i]/weights[i]))
        end
    end

    sort!(recommendations, by=x -> x.score, rev=true)
    result = recommendations[1:min(top_k, length(recommendations))]
    return OmniResult(Dict("recommendations" => result, "n_candidates" => length(recommendations)))
end
