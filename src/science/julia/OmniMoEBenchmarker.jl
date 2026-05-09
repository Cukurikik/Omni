# OMNI Framework - Julia HPC MoE Benchmarker
# Benchmarks floating point throughput of MoE FFN layers using Julia's highly optimized SIMD matrices

module OmniMoEBenchmarker

using LinearAlgebra
using Printf

export benchmark_expert_layer

"""
Simulates an MoE expert's Feed Forward Network and benchmarks its throughput.
Uses Julia's native BLAS (OpenBLAS/MKL) for maximum CPU utilization.
"""
function benchmark_expert_layer(batch_size::Int, seq_len::Int, d_model::Int, d_ff::Int, num_iterations::Int=100)
    println("OMNI Julia (HPC): Initializing MoE FFN Benchmark.")
    @printf("Config: Tokens=%d, d_model=%d, d_ff=%d\n", batch_size*seq_len, d_model, d_ff)

    # Pre-allocate matrices
    num_tokens = batch_size * seq_len
    
    # Random uniform data
    X = rand(Float32, num_tokens, d_model)
    W1 = rand(Float32, d_model, d_ff)
    W2 = rand(Float32, d_ff, d_model)

    # Warmup
    _ = (X * W1) * W2

    println("OMNI Julia (HPC): Warmup complete. Running $num_iterations iterations...")
    
    # Time the core execution
    start_time = time_ns()
    
    for i in 1:num_iterations
        # FFN forward pass (ignoring activation function for raw GEMM benchmark)
        H = X * W1
        Y = H * W2
    end
    
    end_time = time_ns()
    
    duration_sec = (end_time - start_time) / 1e9
    
    # Flops calculation:
    # X * W1 = num_tokens * d_model * d_ff * 2 ops
    # H * W2 = num_tokens * d_ff * d_model * 2 ops
    flops_per_iter = 4.0 * num_tokens * d_model * d_ff
    total_flops = flops_per_iter * num_iterations
    tflops = (total_flops / duration_sec) / 1e12

    @printf("OMNI Julia (HPC): Benchmark Complete.\n")
    @printf("-> Time taken: %.4f seconds\n", duration_sec)
    @printf("-> Throughput: %.2f TFLOPS\n", tflops)
    
    return tflops
end

end # module

# To run:
# using .OmniMoEBenchmarker
# benchmark_expert_layer(8, 2048, 4096, 14336)
