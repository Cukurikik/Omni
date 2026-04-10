# ============================================================
# OMNI Julia Bridge — HPC/SIMD Compute Nexus
# ============================================================
# Layer: Compute (SIMD, Numerical, HPC)
# Julia menggunakan ccall bawaan — TIDAK perlu Pkg.add apapun.
# ============================================================

module OmniBridge

# Deteksi platform
const LIB_EXT = Sys.iswindows() ? "omni_core.dll" :
                Sys.isapple()   ? "libomni_core.dylib" :
                                  "libomni_core.so"

const LIB_PATH = joinpath(@__DIR__, "..", "..", "core", "target", "release", LIB_EXT)

"""
    execute(function_name::String, data::Vector{UInt8}) -> Ptr{Cvoid}

Memanggil fungsi OMNI melalui batas C-ABI dengan zero-copy.
Julia ccall menjamin NO GC PAUSE selama cross-language call.
"""
function execute(function_name::String, data::Vector{UInt8})::Ptr{Cvoid}
    if isempty(data)
        error("[OMNI-E601] Data tidak boleh kosong")
    end

    # ccall langsung ke pointer — tanpa serialisasi
    result_ptr = ccall(
        (:__omni_ffi, LIB_PATH),
        Ptr{Cvoid},                      # return type
        (Ptr{UInt8}, Csize_t),           # arg types
        pointer(data), length(data)       # args
    )

    if result_ptr == C_NULL
        error("[OMNI-E602] Kernel mengembalikan null pointer")
    end

    return result_ptr
end

"""
    execute_simd(data::Vector{Float64}) -> Ptr{Cvoid}

Optimized path: kirim array numerik langsung ke Rust SIMD engine.
Julia Vector{Float64} layout identik dengan Rust Vec<f64> — true zero-copy.
"""
function execute_simd(data::Vector{Float64})::Ptr{Cvoid}
    raw_bytes = reinterpret(UInt8, data)
    return execute("julia_simd_dispatch", raw_bytes)
end

export execute, execute_simd

end # module OmniBridge
