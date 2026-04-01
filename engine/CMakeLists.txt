cmake_minimum_required(VERSION 3.10)
project(TheUltimateFusionEngine)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(media_engine src/media_sync/core.cpp)

# 🧠 OMNI MANIPULATOR: Memory-Mapped File Engine
add_executable(omni_manipulator src/omni_manipulator.cpp)
