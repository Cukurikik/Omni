cmake_minimum_required(VERSION 3.14)
project(OmniAutoDriver CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(omni_auto auto.cpp)

# Optimize for size/speed based on build type
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    if(MSVC)
        target_compile_options(omni_auto PRIVATE /O2)
    else()
        target_compile_options(omni_auto PRIVATE -O3 -flto)
    endif()
endif()
