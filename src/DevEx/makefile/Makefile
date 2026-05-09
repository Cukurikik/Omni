# OMNI Framework - Root Makefile
# Orchestrates the Universal Binary build chain across all polyglot components.

CC = gcc
CXX = g++
ZIG = zig
RUSTC = cargo
GO = go

CFLAGS = -O3 -Wall -fPIC
CXXFLAGS = -O3 -Wall -std=c++17 -fPIC

.PHONY: all c_libs cpp_engine rust_daemons go_gateway clean

all: c_libs cpp_engine rust_daemons go_gateway
	@echo "OMNI Make: Build complete."

c_libs:
	@echo "Building C NUMA and InfiniBand Libraries..."
	$(CC) $(CFLAGS) -c src/system/c/omni_moe_numa_balancer.c -o build/omni_numa.o
	$(CC) $(CFLAGS) -c src/system/c/omni_moe_ib_verbs.c -o build/omni_ib.o

cpp_engine:
	@echo "Building C++ CUDA Graph Engine..."
	$(CXX) $(CXXFLAGS) -c src/compute/cpp/omni_cudagraph_executor.cpp -o build/omni_cudagraph.o

rust_daemons:
	@echo "Building Rust System Daemons..."
	cd src/network/rust/omni_llm_server_launcher && $(RUSTC) build --release

go_gateway:
	@echo "Building Go Ensemble Router..."
	cd src/network/go && $(GO) build -o ../../../build/omni_go_router omni_ensemble_router.go

clean:
	@echo "Cleaning Build Artifacts..."
	rm -rf build/*.o
	cd src/network/rust/omni_llm_server_launcher && $(RUSTC) clean
