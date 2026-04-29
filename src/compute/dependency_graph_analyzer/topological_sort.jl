module DependencyGraphAnalyzer

export OmniResult, compute_topological_sort

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

# Deterministic topological sorting for dependency graph resolution
# Used by the OMNI package manager to resolve build order
function compute_topological_sort(num_nodes::Int, edges::Vector{Tuple{Int, Int}}) :: OmniResult{Vector{Int}, String}
    if num_nodes <= 0
        return OmniResult("Graph must have at least one node", Vector{Int})
    end
    
    in_degree = zeros(Int, num_nodes)
    adj_list = [Int[] for _ in 1:num_nodes]
    
    for (u, v) in edges
        if u < 1 || u > num_nodes || v < 1 || v > num_nodes
            return OmniResult("Edge out of bounds", Vector{Int})
        end
        push!(adj_list[u], v)
        in_degree[v] += 1
    end
    
    queue = Int[]
    for i in 1:num_nodes
        if in_degree[i] == 0
            push!(queue, i)
        end
    end
    
    result = Int[]
    while !isempty(queue)
        u = popfirst!(queue)
        push!(result, u)
        
        for v in adj_list[u]
            in_degree[v] -= 1
            if in_degree[v] == 0
                push!(queue, v)
            end
        end
    end
    
    if length(result) != num_nodes
        return OmniResult("Graph contains a cycle", Vector{Int})
    end
    
    return OmniResult(result)
end

end
