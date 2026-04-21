cmake_minimum_required(VERSION 3.10)

# Force MinGW GCC/G++ compiler if not auto-detected
if(WIN32 AND NOT DEFINED CMAKE_C_COMPILER)
    find_program(GCC_FOUND gcc)
    find_program(GPP_FOUND g++)
    if(GCC_FOUND AND GPP_FOUND)
        set(CMAKE_C_COMPILER "${GCC_FOUND}" CACHE STRING "C compiler")
        set(CMAKE_CXX_COMPILER "${GPP_FOUND}" CACHE STRING "C++ compiler")
    endif()
endif()

project(TheUltimateFusionEngine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Check if source files exist before adding targets
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/src/media_sync/core.cpp")
    add_executable(media_engine src/media_sync/core.cpp)
endif()

# OMNI MANIPULATOR: Memory-Mapped File Engine
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/src/omni_manipulator.cpp")
    add_executable(omni_manipulator src/omni_manipulator.cpp)
endif()
