# Omni TIFA VQA Stats (Julia)
module OmniTIFA
function tifa_score(correct::Vector{Bool})
    isempty(correct) && return 0.0
    sum(correct) / length(correct)
end
function batch_tifa(scores::Vector{Float64})
    isempty(scores) && return (mean=0.0, min=0.0, max=0.0)
    (mean=sum(scores)/length(scores), min=minimum(scores), max=maximum(scores))
end
end
