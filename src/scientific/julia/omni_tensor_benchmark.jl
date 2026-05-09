# OMNI MOTHER: HPC Julia Benchmarks (Production Grade)
using LinearAlgebra

function bench_matmul()
    println("[OMNI JULIA] Initializing MatMul benchmark...")
    
    N = 4096
    A = rand(Float32, N, N)
    B = rand(Float32, N, N)
    
    # Warmup
    C = A * B
    
    # Time it
    t0 = time()
    for i in 1:10
        C = A * B
    end
    t1 = time()
    
    avg_time = (t1 - t0) / 10
    tflops = (2 * N^3) / (avg_time * 1e12)
    
    println("[OMNI JULIA] 4096x4096 Float32 MatMul: $avg_time seconds ($tflops TFLOPS)")
end
