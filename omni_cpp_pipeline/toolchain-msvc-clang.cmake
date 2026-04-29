# Toolchain file for Clang with MSVC libraries

# Set the system name and processor to help CMake detect the platform correctly
set(CMAKE_SYSTEM_NAME Windows)
set(CMAKE_SYSTEM_PROCESSOR AMD64)

# Determine if we're using MSVC runtime
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>DLL")

# Set linker flags to use MSVC-compatible libraries
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -fuse-ld=lld-link")
set(CMAKE_SHARED_LINKER_FLAGS "${CMAKE_SHARED_LINKER_FLAGS} -fuse-ld=lld-link")
set(CMAKE_MODULE_LINKER_FLAGS "${CMAKE_MODULE_LINKER_FLAGS} -fuse-ld=lld-link")

# Configure to use MSVC standard library
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /EHsc /bigobj")