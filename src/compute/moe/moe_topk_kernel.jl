# moe_topk_kernel.jl — High-performance Top-K Kernel
# Layer: Compute / System — MoE SIMD Top-K Selection
#
# Custom Julia SIMD kernel for lightning-fast Top-K selection
# across thousands of expert logits. Essential for routers dealing
# with massive numbers of experts (e.g., 2048+).

module MoETopKKernel

export simd_topk_1d, batch_simd_topk

using LoopVectorization

"""
    simd_topk_1d(logits::Vector{Float32}, k::Int)

Highly optimized Top-K selection for a single token's expert logits.
Returns the indices and values of the top `k` experts.
"""
function simd_topk_1d(logits::Vector{Float32}, k::Int)
    n = length(logits)
    @assert k <= n "k must be <= length(logits)"
    
    # Preallocate output arrays
    top_vals = fill(-Inf32, k)
    top_idx = zeros(Int32, k)
    
    # We use a simple linear scan with an insertion sort for small K
    # which is very fast and SIMD-friendly for small arrays.
    @inbounds for i in 1:n
        val = logits[i]
        
        # If val is smaller than our smallest top-k, skip
        if val > top_vals[k]
            # Find insertion point
            pos = k
            while pos > 1 && val > top_vals[pos-1]
                pos -= 1
            end
            
            # Shift elements down
            for j in k:-1:(pos+1)
                top_vals[j] = top_vals[j-1]
                top_idx[j] = top_idx[j-1]
            end
            
            # Insert new element
            top_vals[pos] = val
            top_idx[pos] = Int32(i - 1) # 0-indexed for interoperability
        end
    end
    
    return top_vals, top_idx
end

"""
    batch_simd_topk(logits_matrix::Matrix{Float32}, k::Int)

Batch processing of Top-K selection.
`logits_matrix` is expected to be sized (num_experts, num_tokens).
Returns a tuple of (top_weights, top_indices) sized (k, num_tokens).
"""
function batch_simd_topk(logits_matrix::Matrix{Float32}, k::Int)
    num_experts, num_tokens = size(logits_matrix)
    
    out_vals = Matrix{Float32}(undef, k, num_tokens)
    out_idx = Matrix{Int32}(undef, k, num_tokens)
    
    # Multi-threaded batch processing
    Threads.@threads for t in 1:num_tokens
        # Extract column view (no copy)
        token_logits = @view logits_matrix[:, t]
        
        top_vals = fill(-Inf32, k)
        top_idx = zeros(Int32, k)
        
        # Optimized core loop using LoopVectorization if applicable
        @inbounds for i in 1:num_experts
            val = token_logits[i]
            if val > top_vals[k]
                pos = k
                while pos > 1 && val > top_vals[pos-1]
                    pos -= 1
                end
                
                for j in k:-1:(pos+1)
                    top_vals[j] = top_vals[j-1]
                    top_idx[j] = top_idx[j-1]
                end
                
                top_vals[pos] = val
                top_idx[pos] = Int32(i - 1)
            end
        end
        
        # Store results
        @inbounds for j in 1:k
            out_vals[j, t] = top_vals[j]
            out_idx[j, t] = top_idx[j]
        end
    end
    
    return out_vals, out_idx
end

end # module
