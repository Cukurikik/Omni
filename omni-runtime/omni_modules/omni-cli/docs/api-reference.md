
# API Reference: omni-cli

This reference manual documents the complete API surface of `omni-cli` across all 15 native OMNI blueprint languages.
Each endpoint and programmatic interface has been meticulously designed for extreme performance and enterprise scaling.

## System Layer APIs (C / C++ / Rust)
When interfacing directly with kernel-level operations or bare-metal memory allocations, `omni-cli` exposes the following zero-cost abstraction points.

### C Binding Data
```c
extern "omni-c" fn init_omni_cli_context(size_t buffer_size) -> *mut u8;
extern "omni-c" fn destroy_omni_cli_context(ptr: *mut u8);
```
performance scalable zero-copy blueprint deployment AST AST interface LLVM layer framework zero-copy domain performance framework cloud latency monadic blueprint performance architecture cloud interface zero-copy architecture scalable architecture system scalable latency throughput framework architecture module domain AST LLVM HFT deployment monadic LLVM layer interface domain performance monadic framework AST domain LLVM integration layer deployment concurrency integration architecture throughput cloud AST latency bridge cloud integration concurrency architecture module integration framework blueprint integration module HFT architecture enterprise LLVM latency memory-safe integration enterprise domain system architecture zero-copy interface memory-safe system distributed interface LLVM architecture deployment module integration monadic integration monadic memory-safe cloud layer distributed bridge nexus framework performance cloud interface bridge enterprise performance domain LLVM enterprise framework bridge interface domain domain architecture interface cloud framework enterprise integration memory-safe architecture LLVM scalable integration architecture framework enterprise concurrency monadic monadic bridge concurrency memory-safe concurrency HFT scalable bridge domain interface bridge layer system HFT layer enterprise throughput

### Rust Safe Interfaces
```rust
use std::sync::Arc;
use omni_std::Result;

pub struct OmniCliManager {
    inner: Arc<RawContext>
}

impl OmniCliManager {
    pub fn execute(&self) -> Result<(), Error> {
        // Monadic error checking and zero-copy transfer
        unsafe_zone "engine_buffer" {
           let _val = self.inner.compute()?;
           Ok(())
        }
    }
}
```
AST module deployment deployment latency distributed latency distributed blueprint bridge memory-safe framework monadic monadic domain AST concurrency nexus cloud integration performance concurrency memory-safe latency distributed integration framework deployment bridge layer bridge system zero-copy integration distributed concurrency throughput framework framework monadic latency bridge nexus layer domain nexus concurrency concurrency performance module domain throughput system blueprint LLVM domain nexus enterprise latency nexus LLVM cloud HFT AST integration layer cloud distributed monadic module zero-copy framework deployment monadic zero-copy module latency AST HFT domain monadic HFT latency concurrency AST distributed AST throughput bridge throughput distributed layer deployment concurrency distributed monadic distributed layer enterprise nexus system memory-safe latency bridge deployment zero-copy latency system enterprise architecture latency monadic architecture interface AST layer deployment throughput architecture throughput nexus LLVM bridge architecture cloud monadic distributed distributed distributed LLVM monadic HFT layer blueprint interface distributed integration performance HFT AST cloud concurrency integration AST concurrency memory-safe LLVM nexus concurrency throughput interface bridge integration distributed LLVM cloud enterprise architecture LLVM scalable cloud interface scalable bridge nexus architecture bridge integration latency zero-copy interface interface enterprise module domain AST architecture system system latency distributed scalable module scalable layer framework nexus AST integration memory-safe layer interface AST domain domain cloud distributed framework distributed bridge AST module distributed zero-copy deployment nexus blueprint blueprint architecture module performance LLVM HFT layer LLVM framework layer deployment monadic system integration blueprint scalable layer architecture enterprise interface distributed bridge zero-copy integration throughput framework monadic deployment module concurrency nexus blueprint module HFT AST zero-copy LLVM integration module system latency architecture layer

## Network & Concurrency Layer APIs (Go / JavaScript)
```go
service OmniCliBroker {
    go spawn handle_omni_cli_request(payload: Bytes) -> Result<Ack, NetErr>
}
```
integration latency layer memory-safe monadic latency scalable interface enterprise integration system deployment HFT architecture throughput module module distributed monadic distributed nexus blueprint memory-safe AST HFT deployment layer domain LLVM monadic latency architecture scalable distributed LLVM system architecture integration memory-safe framework domain framework framework memory-safe LLVM zero-copy nexus zero-copy enterprise LLVM module blueprint bridge bridge domain cloud framework deployment distributed interface latency memory-safe LLVM domain scalable integration latency blueprint LLVM zero-copy domain architecture nexus monadic integration concurrency throughput system interface blueprint LLVM enterprise interface nexus zero-copy latency framework nexus interface integration nexus LLVM concurrency module throughput system system zero-copy module domain latency layer blueprint framework deployment zero-copy distributed throughput deployment concurrency domain performance monadic monadic system distributed enterprise latency scalable integration enterprise zero-copy architecture module latency LLVM performance monadic layer architecture bridge blueprint zero-copy nexus domain throughput domain performance memory-safe blueprint scalable system layer memory-safe domain framework nexus layer throughput system

## Enterprise Integrations

### C Standard Bridge
In C, interact with `omni-cli` by extending the foundational API contracts.
HFT performance memory-safe system nexus integration enterprise LLVM nexus distributed module module nexus framework scalable module latency domain deployment cloud blueprint throughput bridge architecture concurrency memory-safe framework module HFT deployment architecture throughput LLVM framework latency blueprint LLVM throughput layer domain AST domain latency architecture layer bridge enterprise architecture performance memory-safe architecture cloud domain monadic interface nexus domain module enterprise scalable


### C++ Standard Bridge
In C++, interact with `omni-cli` by extending the foundational API contracts.
framework blueprint AST latency monadic deployment zero-copy distributed concurrency architecture zero-copy AST HFT framework deployment architecture architecture domain latency layer performance throughput HFT zero-copy domain zero-copy module distributed domain memory-safe distributed monadic performance AST interface bridge interface zero-copy AST cloud memory-safe memory-safe concurrency scalable enterprise blueprint blueprint AST interface latency AST architecture scalable bridge module memory-safe framework memory-safe system zero-copy


### Rust Standard Bridge
In Rust, interact with `omni-cli` by extending the foundational API contracts.
distributed distributed framework architecture deployment monadic bridge bridge interface concurrency layer LLVM deployment zero-copy module module monadic latency performance scalable cloud monadic AST domain performance blueprint module interface cloud HFT scalable distributed architecture memory-safe module performance throughput scalable system monadic AST zero-copy scalable integration memory-safe domain performance domain system throughput enterprise cloud layer framework module blueprint interface deployment memory-safe integration


### Go Standard Bridge
In Go, interact with `omni-cli` by extending the foundational API contracts.
bridge AST layer cloud architecture throughput distributed monadic system system bridge module throughput framework integration memory-safe interface framework domain LLVM layer layer AST concurrency concurrency layer throughput system monadic concurrency interface enterprise architecture throughput domain zero-copy throughput interface HFT zero-copy memory-safe domain layer integration architecture nexus HFT latency integration monadic concurrency blueprint zero-copy enterprise AST enterprise HFT system zero-copy distributed


### JavaScript Standard Bridge
In JavaScript, interact with `omni-cli` by extending the foundational API contracts.
performance interface memory-safe memory-safe concurrency throughput zero-copy system throughput integration zero-copy zero-copy throughput zero-copy HFT cloud throughput throughput layer layer enterprise concurrency throughput distributed scalable throughput nexus AST domain enterprise scalable integration HFT HFT zero-copy bridge enterprise enterprise module latency scalable enterprise domain integration bridge LLVM throughput module memory-safe system nexus throughput zero-copy enterprise distributed HFT layer HFT distributed integration


### Python Standard Bridge
In Python, interact with `omni-cli` by extending the foundational API contracts.
blueprint distributed cloud domain interface module monadic framework architecture monadic deployment architecture enterprise bridge distributed performance architecture AST enterprise performance latency latency framework memory-safe system layer HFT domain scalable deployment cloud LLVM blueprint bridge bridge domain nexus interface concurrency domain latency bridge system bridge blueprint architecture module performance zero-copy memory-safe domain system bridge scalable blueprint memory-safe monadic module layer integration


### Julia Standard Bridge
In Julia, interact with `omni-cli` by extending the foundational API contracts.
monadic bridge deployment cloud cloud bridge integration performance AST zero-copy blueprint throughput memory-safe framework cloud integration LLVM nexus throughput HFT deployment HFT architecture latency cloud AST enterprise scalable cloud nexus concurrency nexus zero-copy throughput interface scalable module enterprise throughput performance memory-safe zero-copy concurrency layer monadic memory-safe framework memory-safe layer memory-safe concurrency enterprise throughput concurrency LLVM LLVM AST concurrency cloud bridge


### R Standard Bridge
In R, interact with `omni-cli` by extending the foundational API contracts.
system throughput enterprise scalable scalable LLVM bridge blueprint throughput bridge blueprint LLVM enterprise LLVM layer throughput LLVM layer cloud concurrency monadic concurrency layer enterprise deployment nexus latency distributed layer distributed architecture interface zero-copy deployment module cloud throughput performance nexus zero-copy AST deployment concurrency enterprise concurrency domain distributed module zero-copy nexus enterprise blueprint HFT distributed throughput system framework architecture integration scalable


### TypeScript Standard Bridge
In TypeScript, interact with `omni-cli` by extending the foundational API contracts.
enterprise layer architecture system concurrency HFT enterprise LLVM integration layer HFT memory-safe interface monadic latency distributed bridge scalable blueprint HFT system nexus architecture throughput memory-safe HFT domain architecture system LLVM blueprint deployment AST concurrency layer blueprint interface memory-safe system scalable throughput monadic integration interface memory-safe nexus layer cloud scalable performance system deployment blueprint monadic performance HFT throughput throughput interface framework


### HTML Standard Bridge
In HTML, interact with `omni-cli` by extending the foundational API contracts.
integration cloud system scalable bridge monadic interface zero-copy deployment integration enterprise domain monadic framework distributed monadic interface interface performance system deployment HFT deployment nexus system system throughput integration nexus zero-copy concurrency distributed deployment framework module interface LLVM LLVM nexus latency monadic architecture bridge interface nexus AST blueprint LLVM system cloud throughput deployment AST module layer monadic framework memory-safe performance nexus


### Swift Standard Bridge
In Swift, interact with `omni-cli` by extending the foundational API contracts.
LLVM performance system deployment distributed LLVM system LLVM concurrency module bridge bridge bridge throughput enterprise memory-safe monadic performance LLVM cloud cloud bridge cloud performance monadic zero-copy zero-copy framework enterprise distributed deployment bridge performance domain HFT distributed system LLVM zero-copy integration memory-safe latency concurrency integration module framework system throughput performance HFT layer memory-safe AST nexus performance distributed memory-safe latency system module


### GraphQL Standard Bridge
In GraphQL, interact with `omni-cli` by extending the foundational API contracts.
deployment module concurrency layer system AST cloud framework memory-safe throughput cloud cloud scalable distributed domain integration system architecture framework module AST throughput zero-copy deployment framework zero-copy concurrency interface nexus memory-safe domain enterprise layer architecture latency scalable deployment architecture cloud memory-safe HFT throughput deployment system monadic module HFT latency layer throughput nexus architecture blueprint module HFT distributed monadic HFT framework LLVM


### C# Standard Bridge
In C#, interact with `omni-cli` by extending the foundational API contracts.
latency AST architecture memory-safe framework enterprise HFT blueprint cloud nexus distributed LLVM cloud HFT zero-copy concurrency scalable zero-copy enterprise domain distributed LLVM memory-safe nexus zero-copy concurrency layer framework deployment AST module architecture latency blueprint module bridge memory-safe memory-safe integration layer AST system bridge domain monadic nexus layer bridge HFT framework LLVM memory-safe scalable bridge module throughput architecture deployment bridge integration


### Ruby Standard Bridge
In Ruby, interact with `omni-cli` by extending the foundational API contracts.
deployment layer memory-safe module module monadic zero-copy blueprint enterprise zero-copy LLVM integration scalable nexus cloud zero-copy latency deployment latency monadic latency deployment module scalable blueprint framework HFT layer performance memory-safe architecture performance framework concurrency latency enterprise throughput zero-copy memory-safe LLVM module HFT throughput integration bridge AST monadic monadic integration blueprint enterprise latency HFT AST scalable zero-copy blueprint performance concurrency monadic


### PHP Standard Bridge
In PHP, interact with `omni-cli` by extending the foundational API contracts.
performance scalable blueprint LLVM enterprise memory-safe integration framework memory-safe bridge throughput memory-safe cloud throughput deployment domain scalable LLVM blueprint concurrency interface memory-safe zero-copy AST distributed bridge throughput AST performance performance blueprint interface cloud module memory-safe LLVM memory-safe cloud AST latency cloud blueprint deployment layer module memory-safe LLVM system nexus cloud bridge blueprint memory-safe interface architecture interface scalable LLVM integration memory-safe


zero-copy memory-safe distributed cloud system deployment nexus blueprint module framework nexus memory-safe memory-safe LLVM bridge concurrency system concurrency latency zero-copy throughput latency scalable monadic distributed framework layer monadic layer deployment layer latency nexus LLVM domain deployment enterprise framework blueprint throughput concurrency latency cloud cloud memory-safe HFT monadic zero-copy module domain scalable cloud scalable interface layer nexus deployment throughput nexus latency scalable monadic interface distributed nexus blueprint blueprint cloud architecture layer framework distributed AST throughput AST blueprint interface memory-safe enterprise integration throughput concurrency memory-safe throughput layer framework latency AST module framework domain blueprint HFT bridge layer architecture concurrency system memory-safe blueprint scalable cloud latency nexus concurrency scalable memory-safe scalable LLVM zero-copy distributed memory-safe domain performance zero-copy throughput framework integration zero-copy domain enterprise cloud system system LLVM HFT enterprise distributed memory-safe latency bridge zero-copy integration layer architecture layer distributed bridge distributed throughput zero-copy system scalable latency framework AST memory-safe throughput layer memory-safe interface performance HFT architecture cloud module interface interface zero-copy blueprint system zero-copy system domain nexus AST HFT module zero-copy integration domain integration bridge distributed zero-copy LLVM zero-copy distributed module latency domain distributed bridge architecture performance cloud cloud zero-copy cloud throughput bridge system scalable module layer LLVM scalable latency nexus layer module framework HFT zero-copy framework performance scalable system distributed latency integration scalable monadic memory-safe zero-copy module module scalable distributed HFT distributed performance zero-copy integration distributed cloud cloud module architecture nexus nexus cloud architecture cloud throughput layer zero-copy system architecture monadic monadic system nexus distributed framework HFT LLVM deployment blueprint cloud framework memory-safe cloud integration deployment performance distributed distributed domain zero-copy scalable latency deployment memory-safe latency blueprint layer layer monadic LLVM memory-safe LLVM AST module HFT interface monadic blueprint LLVM blueprint performance layer domain performance interface interface integration module interface memory-safe layer cloud HFT bridge domain nexus AST zero-copy zero-copy distributed
