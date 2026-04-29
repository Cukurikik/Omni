module FugueCompute

struct OmniResult{T, E}
    value::Union{T, Nothing}
    error::Union{E, Nothing}
end

function is_ok(res::OmniResult)::Bool
    return res.error === nothing
end

struct TaskNode
    id::String
    dependencies::Vector{String}
end

function schedule_dag(tasks::Vector{TaskNode})::OmniResult{Vector{Vector{String}}, String}
    if isempty(tasks)
        return OmniResult{Vector{Vector{String}}, String}(nothing, "Task list is empty")
    end

    # Deterministic mathematical topological sort for DAG scheduling
    in_degree = Dict{String, Int}()
    adj_list = Dict{String, Vector{String}}()
    
    for task in tasks
        in_degree[task.id] = 0
        adj_list[task.id] = []
    end
    
    for task in tasks
        for dep in task.dependencies
            if haskey(adj_list, dep)
                push!(adj_list[dep], task.id)
                in_degree[task.id] += 1
            else
                return OmniResult{Vector{Vector{String}}, String}(nothing, "Missing dependency: " * dep)
            end
        end
    end

    execution_layers = Vector{Vector{String}}()
    queue = String[]
    
    for (node, deg) in in_degree
        if deg == 0
            push!(queue, node)
        end
    end

    # Sort queue deterministically
    sort!(queue)

    while !isempty(queue)
        current_layer = String[]
        next_queue = String[]
        
        for u in queue
            push!(current_layer, u)
            for v in adj_list[u]
                in_degree[v] -= 1
                if in_degree[v] == 0
                    push!(next_queue, v)
                end
            end
        end
        
        sort!(next_queue)
        push!(execution_layers, current_layer)
        queue = next_queue
    end

    # Check for cycles
    executed_count = sum(length(layer) for layer in execution_layers)
    if executed_count != length(tasks)
        return OmniResult{Vector{Vector{String}}, String}(nothing, "Cycle detected in DAG")
    end

    return OmniResult{Vector{Vector{String}}, String}(execution_layers, nothing)
end

end
