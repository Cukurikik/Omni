module Omni.Compute.FedML.Aggregator

# OMNI FEDML: Federated Averaging (FedAvg) Mathematical Core
# High-performance Julia weight aggregation using BLAS.
# Source: FedML-AI/FedML

struct AggregationError <: Exception
    msg::String
end

"""
    federated_averaging(client_weights::Vector{Vector{Float64}}, sample_sizes::Vector{Int})

Performs the FedAvg algorithm: w_global = sum( (n_k / n) * w_k )
"""
function federated_averaging(client_weights::Vector{Vector{Float64}}, sample_sizes::Vector{Int})::Union{Vector{Float64}, AggregationError}
    num_clients = length(client_weights)
    
    if num_clients == 0
        return AggregationError("No client weights provided.")
    end
    
    if num_clients != length(sample_sizes)
        return AggregationError("Mismatch between number of weight vectors and sample sizes.")
    end
    
    vec_len = length(client_weights[1])
    for w in client_weights
        if length(w) != vec_len
            return AggregationError("All client weight vectors must have the same dimension.")
        end
    end
    
    total_samples = sum(sample_sizes)
    if total_samples <= 0
        return AggregationError("Total samples must be positive.")
    end
    
    # Initialize global model vector
    global_weights = zeros(Float64, vec_len)
    
    # Perform weighted sum
    for k in 1:num_clients
        weight_factor = sample_sizes[k] / total_samples
        # Fast BLAS vector addition
        global_weights .+= client_weights[k] .* weight_factor
    end
    
    return global_weights
end

end # module
