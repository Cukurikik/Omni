# System Layer Deep Reference

## ARM Processor Hierarchy
- Cortex-M (microcontroller): M0, M0+, M3, M4, M7, M23, M33, M35P, M55, M85
- Cortex-R (real-time): R4, R5, R7, R8, R52, R82
- Cortex-A (application): A5, A7, A8, A9, A12, A15, A17, A32-A78AE, X1-X4
- Neoverse (server): N1, N2, V1, V2, E1, E2, E3
- Mali/Immortalis: GPU cores
- Ethos: NPU cores untuk AI inference
- Corstone: complete subsystem reference designs

## CHERI & Memory Safety Architecture
CHERI (Capability Hardware Enhanced RISC Instructions) menambahkan capability-based
addressing ke ISA konvensional. Pointer menjadi "capabilities" yang mengandung:
- Base address
- Bounds (length)
- Permissions (read/write/execute/seal)
- Valid bit (tidak bisa dipalsukan)

Platform:
- ARM Morello: CHERI prototype di Neoverse N1 SoC
- CHERI-RISC-V: open-source reference implementation
- CHERI-MIPS: implementasi awal (penelitian Cambridge)
- CheriBSD: FreeBSD port untuk Morello

Bahasa yang mendukung CHERI:
- C/C++ dengan __capability qualifier
- Rust (memory safety model komplementer)
- Python, Ruby, PHP, Node.js (sudah diport ke Morello)

## Formal Verification Tools

### Deductive Verification
- Dafny: pre/postconditions, loop invariants, verified code generation
- VeriFast: separation logic untuk C dan Java
- Frama-C: C code analysis (Jessie, WP, Value plugins)
- Boogie: intermediate verification language (dipakai Dafny, VCC)
- Why3: platform untuk deductive verification (dipakai Krakatoa, Jessie)

### Type-Theoretic Proof Assistants
- Coq: Calculus of Constructions, dipakai untuk CompCert (verified C compiler)
- Isabelle/HOL: Higher-Order Logic, dipakai untuk seL4 verification
- Lean 4: modern proof assistant + programming language
- Agda: dependent types, propositions-as-types
- Idris 2: practical dependent types dengan effects system

### Model Checking
- TLA+/PlusCal: temporal logic, dipakai Amazon (DynamoDB, S3) dan Microsoft
- Alloy: relational logic, lightweight formal modeling
- UPPAAL: timed automata, real-time systems verification
- SPIN/Promela: concurrent systems, LTL properties
- NuSMV/nuXmv: symbolic model checking, BDD/SAT-based

### Rust-Specific Verification
- RustBelt: semantic foundations (RaLo, Iris framework)
- RefinedRust: refinement types untuk Rust
- Prusti: Viper-based verifier untuk Rust
- Creusot: deductive verifier, generates Why3 VCs
- Flux: liquid type inference untuk Rust
- Aeneas: translates Rust ke HOL (Lean/Coq/F*)
- Gillian: compositional symbolic execution

## RTOS Comparison

| RTOS | License | Language | Priority | Use Case |
|------|---------|----------|---------|----------|
| FreeRTOS | MIT | C | Preemptive | General embedded |
| Zephyr | Apache 2 | C | Preemptive | IoT, connected |
| seL4 | GPL/Commercial | C | Preemptive | Safety-critical |
| RIOT | LGPL | C/C++ | Preemptive | IoT constrained |
| NuttX | Apache 2 | C | Preemptive | POSIX-compliant |
| ThreadX | MIT (Azure) | C | Preemptive | Azure IoT |
| QNX | Commercial | C | Preemptive | Automotive (ADAS) |
| Integrity | Commercial | C | Partitioned | Aerospace DO-178 |
| VxWorks | Commercial | C | Preemptive | Defense, aerospace |
| Mbed OS | Apache 2 | C++ | Preemptive | ARM Cortex-M |

## Microarchitecture Simulators

| Simulator | Focus | Language |
|-----------|-------|----------|
| gem5 | Full system | Python+C++ |
| Simics | Full system | Proprietary |
| QEMU | Full system | C |
| ZSim | Multicore | C++ |
| Sniper | Multicore | C++ |
| Accel-Sim | GPU | C++ |
| GPGPU-Sim | GPU | C++ |
| McPAT | Power/Area | C++ |
| CACTI | Cache | C++ |
| DRAMSim2 | DRAM | C++ |
| Ramulator | DRAM | C++ |
