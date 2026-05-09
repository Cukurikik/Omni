# Formal Methods Reference

## When to Use Formal Verification

| Risk Level | Domain | Recommended Approach |
|------------|--------|---------------------|
| Ultra-high | Medical devices, aircraft, nuclear | Isabelle/HOL + DO-178C/IEC 61508 |
| Very high | Automotive ADAS, railway signaling | Frama-C + MISRA C, UPPAAL |
| High | Cryptographic protocols, financial | Tamarin, TLA+, Dafny |
| Medium | Distributed systems, blockchain | TLA+, Alloy, Solidity auditing |
| Low | Business logic | Property-based testing (QuickCheck) |

## Protocol Verification

### Tamarin Prover
- Multiset rewriting + first-order logic
- Supports Diffie-Hellman, XOR, multiset
- Verified: TLS 1.3, Signal Protocol, 5G AKA, OAuth

### ProVerif
- Applied pi-calculus based
- Automatic, but less expressive than Tamarin
- Verified: SSH, TLS 1.2, EAP-TLS

### AVISPA/SPAN
- Older but widely used in academia
- HLPSL language

## Property-Based Testing (Bridge between testing and verification)

- QuickCheck (Haskell) — original, 1999
- Hypothesis (Python) — stateful testing, strategies
- Proptest (Rust) — shrinking, derive macros
- FsCheck (F#/.NET) — QuickCheck port
- ScalaCheck (Scala) — Akka, Kafka testing
- fast-check (TypeScript) — web/Node.js

## Separation Logic Tools

Used to verify programs with pointers and heap:
- VeriFast: C and Java, manual specs
- Iris: Coq framework, used in RustBelt
- Viper: intermediate verification language
  - Prusti → Viper (for Rust)
  - Nagini → Viper (for Python)
  - Carbon → Viper (for Go, experimental)

## VDM and Z (Classical Formal Methods)

- VDM-SL, VDM++: Vienna Development Method, Overture tool
- Z notation: schema-based, widely used in UK standards
- RAISE: algebraic specification

## Safety Standards and Their Tools

| Standard | Domain | Languages | Tools |
|----------|--------|-----------|-------|
| DO-178C | Aviation | Ada, C | GNAT Pro, Frama-C |
| IEC 61508 | Industrial | C, C++, Ada | PolySpace |
| ISO 26262 | Automotive | C, C++, Rust | Frama-C, MISRA |
| IEC 62443 | Industrial Cybersec | Multiple | Multiple |
| WCET Analysis | Real-time | C | aiT, Bound-T |
