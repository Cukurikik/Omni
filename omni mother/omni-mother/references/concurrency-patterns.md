# Concurrency Patterns Cross-Language Reference

## Fundamental Models

| Model | Description | Best Languages |
|-------|-------------|---------------|
| Shared Memory | Threads + locks/mutexes | C, C++, Java, Rust |
| Message Passing | No shared state, channels | Go, Erlang, Rust (channels) |
| Actor Model | Independent actors, mailboxes | Erlang, Elixir, Akka, Pony |
| CSP | Communicating Sequential Processes | Go, occam, Clojure core.async |
| STM | Software Transactional Memory | Haskell, Clojure, Scala |
| Dataflow | Values flow through graph | LabVIEW, Faust, Lucid |
| Reactive | Event streams + backpressure | RxJava, Akka Streams, Reactor |
| Coroutines/Fibers | Cooperative, lightweight | Kotlin, Python, Lua, Ruby |
| Green Threads | Runtime-managed M:N threads | Go goroutines, Erlang processes |
| Async/Await | Syntactic sugar over futures | Rust, Python, JS, C#, Kotlin |

## GPU Computing Models

| API | Vendor | Language | Use Case |
|-----|--------|----------|---------|
| CUDA | NVIDIA | C/C++/Python | Deep learning, HPC |
| OpenCL | Khronos | C kernel | Cross-vendor GPU |
| SYCL | Khronos | C++17 | Intel-led, oneAPI |
| HIP | AMD | C/C++ | ROCm, CUDA portability |
| Metal | Apple | C++14-like | Apple Silicon GPU |
| Vulkan Compute | Khronos | GLSL/HLSL | Cross-platform |
| WebGPU | W3C | WGSL | Browser GPU |
| Taichi | Open | Python | Physical simulation |
| Halide | MIT | C++ embedded | Image processing |
| Triton | OpenAI | Python | ML kernel development |

## Distributed Computing Paradigms

### MapReduce Family
- Hadoop MapReduce (Java)
- Apache Spark (Scala/Python/R/Java)
- Apache Flink (Java/Scala, streaming)
- Apache Beam (unified batch+stream)

### BSP (Bulk Synchronous Parallel)
- BSPlib (C/Fortran)
- MulticoreBSP (C)
- Pregel (Google), Giraph (Apache) → BSP for graphs

### PGAS (Partitioned Global Address Space)
- UPC (C extension)
- Co-Array Fortran
- Chapel (HPE)
- X10 (IBM Research)
- Titanium (Berkeley)

### Actor Frameworks by Language

| Language | Framework | Notes |
|----------|-----------|-------|
| Scala/Java | Akka | Industry standard JVM actors |
| Erlang | Built-in | Battle-tested 30+ years |
| Elixir | Built-in | Erlang VM, better syntax |
| Rust | Actix | Web framework + actors |
| Python | Ray | Distributed ML/compute |
| Go | — | Goroutines + channels (CSP) |
| C++ | CAF | C++ Actor Framework |
| .NET | Orleans | Virtual actors (grains) |
| Pony | Built-in | Reference capabilities, no data races |

## Concurrency Safety Guarantees

| Language | Memory Safety | Data Race Freedom | How |
|----------|--------------|-------------------|-----|
| Rust | Yes | Yes (compile-time) | Ownership + borrow checker |
| Pony | Yes | Yes (compile-time) | Reference capabilities |
| Erlang | Yes (per process) | Yes (immutable) | No shared state |
| Haskell | Yes | Mostly (STM helps) | Immutability + type system |
| Go | Yes | No (runtime race detector) | Goroutines + -race flag |
| Java | Yes (GC) | No (synchronized) | Manual synchronization |
| C++ | No | No | Manual everything |
| C | No | No | Manual everything |
