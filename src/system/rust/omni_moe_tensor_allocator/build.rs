// OMNI Framework - Rust Build Script for MoE Tensor Allocator
// Links the CUDA driver library for FFI calls to cudaHostAlloc

fn main() {
    println!("cargo:rerun-if-changed=src/lib.rs");

    // In a real build environment, this points to the local CUDA toolkit installation
    let cuda_lib_path = option_env!("CUDA_LIB_PATH").unwrap_or("/usr/local/cuda/lib64");
    
    println!("cargo:rustc-link-search=native={}", cuda_lib_path);
    println!("cargo:rustc-link-lib=dylib=cuda");
    println!("cargo:rustc-link-lib=dylib=cudart");
    
    // Warn if CUDA path doesn't exist, but don't fail for the sake of language server parsing
    if !std::path::Path::new(cuda_lib_path).exists() {
        println!("cargo:warning=OMNI Rust Build: CUDA library path not found at {}. FFI bindings may fail at runtime.", cuda_lib_path);
    }
}
