// OMNI System Layer — CMakeLists for GPU kernel compilation
// Build CUDA attention and GEMM kernels

cmake_minimum_required(VERSION 3.18)
project(omni_gpu_kernels CUDA CXX)

set(CMAKE_CUDA_STANDARD 17)
set(CMAKE_CXX_STANDARD 17)

# Detect GPU architecture
include(FindCUDA)
set(CMAKE_CUDA_ARCHITECTURES 70 75 80 86 89 90)

# Source files
set(KERNEL_HEADERS
    attention_kernel.cuh
    gemm_kernel.cuh
)

# Build shared library
add_library(omni_kernels SHARED
    kernel_launcher.cu
)

target_include_directories(omni_kernels PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CUDA_INCLUDE_DIRS}
)

target_compile_options(omni_kernels PRIVATE
    $<$<COMPILE_LANGUAGE:CUDA>:
        --use_fast_math
        -O3
        --generate-line-info
        -Xptxas=-v
    >
)

target_link_libraries(omni_kernels
    ${CUDA_LIBRARIES}
    ${CUDA_CUBLAS_LIBRARIES}
)

# Install
install(TARGETS omni_kernels DESTINATION lib)
install(FILES ${KERNEL_HEADERS} DESTINATION include/omni/gpu)

message(STATUS "OMNI GPU Kernels configured for architectures: ${CMAKE_CUDA_ARCHITECTURES}")
