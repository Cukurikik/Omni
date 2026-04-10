
# API Reference: omni-cli-audit

This reference manual documents the complete API surface of `omni-cli-audit` across all 15 native OMNI blueprint languages.
Each endpoint and programmatic interface has been meticulously designed for extreme performance and enterprise scaling.

## System Layer APIs (C / C++ / Rust)
When interfacing directly with kernel-level operations or bare-metal memory allocations, `omni-cli-audit` exposes the following zero-cost abstraction points.

### C Binding Data
```c
extern "omni-c" fn init_omni_cli_audit_context(size_t buffer_size) -> *mut u8;
extern "omni-c" fn destroy_omni_cli_audit_context(ptr: *mut u8);
```
bridge domain latency architecture system nexus architecture distributed enterprise architecture framework performance HFT LLVM scalable latency bridge distributed blueprint enterprise deployment module domain scalable distributed interface memory-safe scalable enterprise distributed system integration LLVM memory-safe throughput module concurrency enterprise monadic module blueprint cloud zero-copy memory-safe throughput AST domain zero-copy deployment LLVM AST memory-safe LLVM monadic zero-copy memory-safe domain memory-safe memory-safe framework architecture throughput module module latency layer zero-copy enterprise layer domain latency concurrency framework enterprise cloud performance memory-safe layer concurrency architecture layer enterprise distributed layer module memory-safe interface domain AST layer monadic throughput concurrency domain blueprint module scalable module memory-safe blueprint bridge architecture HFT nexus deployment nexus interface bridge latency performance cloud distributed system domain zero-copy distributed domain integration deployment nexus zero-copy interface domain AST monadic cloud scalable monadic domain module enterprise nexus latency enterprise zero-copy monadic monadic architecture AST distributed latency enterprise cloud layer scalable memory-safe distributed zero-copy integration system

### Rust Safe Interfaces
```rust
use std::sync::Arc;
use omni_std::Result;

pub struct OmniCliAuditManager {
    inner: Arc<RawContext>
}

impl OmniCliAuditManager {
    pub fn execute(&self) -> Result<(), Error> {
        // Monadic error checking and zero-copy transfer
        unsafe_zone "engine_buffer" {
           let _val = self.inner.compute()?;
           Ok(())
        }
    }
}
```
AST AST LLVM latency distributed interface performance concurrency LLVM nexus enterprise system nexus LLVM layer scalable cloud framework scalable latency monadic cloud scalable bridge throughput cloud distributed distributed layer deployment memory-safe HFT enterprise concurrency distributed architecture HFT nexus layer AST scalable HFT scalable system blueprint monadic domain LLVM latency AST framework AST latency zero-copy bridge latency HFT HFT zero-copy architecture concurrency memory-safe module zero-copy integration cloud deployment framework memory-safe concurrency distributed layer domain interface HFT blueprint system latency scalable scalable latency memory-safe nexus HFT latency performance nexus latency zero-copy module concurrency memory-safe deployment domain LLVM architecture HFT LLVM throughput cloud domain monadic HFT AST module bridge bridge domain architecture concurrency domain module system enterprise HFT deployment nexus bridge throughput HFT module cloud HFT monadic memory-safe zero-copy framework system deployment bridge cloud architecture enterprise interface monadic interface monadic LLVM throughput nexus framework nexus system latency system nexus HFT integration architecture system HFT LLVM memory-safe architecture deployment concurrency bridge cloud deployment zero-copy blueprint distributed throughput nexus architecture monadic framework memory-safe domain LLVM deployment performance zero-copy cloud interface architecture blueprint nexus throughput integration zero-copy performance concurrency domain throughput interface architecture module module layer enterprise concurrency nexus cloud domain deployment integration memory-safe zero-copy integration bridge module concurrency LLVM system deployment cloud layer AST monadic bridge domain zero-copy interface interface enterprise LLVM layer bridge throughput deployment domain blueprint integration architecture integration layer interface zero-copy HFT integration nexus LLVM latency system latency blueprint cloud integration scalable interface throughput distributed module interface bridge LLVM cloud deployment architecture

## Network & Concurrency Layer APIs (Go / JavaScript)
```go
service OmniCliAuditBroker {
    go spawn handle_omni_cli_audit_request(payload: Bytes) -> Result<Ack, NetErr>
}
```
scalable system integration layer framework LLVM concurrency monadic interface throughput AST integration integration interface cloud framework framework throughput distributed nexus LLVM interface scalable system interface latency distributed integration module module deployment framework distributed bridge module system throughput enterprise blueprint distributed scalable concurrency deployment enterprise LLVM system interface bridge HFT system deployment performance module framework scalable concurrency interface bridge integration deployment cloud memory-safe AST memory-safe memory-safe performance memory-safe system distributed latency blueprint HFT blueprint scalable bridge zero-copy architecture framework concurrency domain system interface interface latency module latency distributed cloud AST architecture performance enterprise framework deployment memory-safe nexus nexus interface blueprint blueprint blueprint system deployment latency HFT architecture throughput scalable HFT nexus monadic nexus latency scalable scalable integration zero-copy memory-safe framework layer module layer framework LLVM module scalable monadic domain module distributed distributed scalable module monadic system framework enterprise system interface deployment framework module interface system deployment cloud latency module blueprint system

## Enterprise Integrations

### C Standard Bridge
In C, interact with `omni-cli-audit` by extending the foundational API contracts.
nexus deployment AST zero-copy deployment framework architecture architecture throughput architecture AST memory-safe HFT module module performance zero-copy bridge architecture bridge throughput distributed LLVM scalable LLVM bridge monadic architecture blueprint integration architecture framework module framework integration module LLVM scalable blueprint LLVM blueprint AST deployment interface blueprint scalable blueprint latency system deployment distributed latency distributed latency architecture AST monadic HFT architecture cloud


### C++ Standard Bridge
In C++, interact with `omni-cli-audit` by extending the foundational API contracts.
system AST zero-copy layer interface throughput system distributed concurrency monadic HFT memory-safe LLVM AST integration throughput blueprint deployment architecture AST framework nexus module cloud domain HFT enterprise architecture architecture architecture layer architecture deployment blueprint scalable framework HFT LLVM framework interface system blueprint scalable zero-copy LLVM monadic enterprise enterprise architecture blueprint interface blueprint deployment interface cloud system monadic framework zero-copy throughput


### Rust Standard Bridge
In Rust, interact with `omni-cli-audit` by extending the foundational API contracts.
domain deployment bridge cloud distributed deployment AST enterprise framework AST blueprint layer interface LLVM throughput architecture throughput bridge performance nexus latency throughput blueprint zero-copy integration nexus nexus interface architecture system distributed domain throughput throughput layer concurrency enterprise blueprint latency architecture interface blueprint throughput blueprint memory-safe cloud HFT performance enterprise zero-copy deployment domain module enterprise LLVM framework nexus LLVM scalable LLVM


### Go Standard Bridge
In Go, interact with `omni-cli-audit` by extending the foundational API contracts.
bridge deployment scalable cloud scalable module latency LLVM integration zero-copy bridge latency framework system cloud zero-copy LLVM AST enterprise deployment blueprint enterprise system bridge monadic latency latency layer concurrency architecture throughput nexus deployment enterprise bridge layer domain bridge integration layer HFT integration cloud architecture domain deployment interface latency deployment cloud HFT concurrency architecture deployment memory-safe LLVM concurrency deployment throughput system


### JavaScript Standard Bridge
In JavaScript, interact with `omni-cli-audit` by extending the foundational API contracts.
module interface system memory-safe nexus AST cloud distributed LLVM layer latency scalable cloud AST integration distributed zero-copy latency system nexus nexus memory-safe module architecture integration interface blueprint cloud bridge zero-copy AST distributed distributed blueprint throughput distributed architecture domain deployment latency LLVM blueprint memory-safe deployment performance interface scalable latency deployment concurrency architecture enterprise bridge blueprint AST domain scalable HFT monadic performance


### Python Standard Bridge
In Python, interact with `omni-cli-audit` by extending the foundational API contracts.
nexus nexus framework LLVM blueprint enterprise cloud AST latency latency module zero-copy framework latency enterprise concurrency HFT enterprise latency domain integration integration distributed bridge nexus scalable LLVM nexus system layer integration interface system system distributed layer concurrency layer integration system monadic latency deployment throughput interface zero-copy HFT throughput latency enterprise monadic cloud enterprise module bridge distributed framework memory-safe system distributed


### Julia Standard Bridge
In Julia, interact with `omni-cli-audit` by extending the foundational API contracts.
interface performance enterprise throughput nexus HFT layer memory-safe nexus scalable module module AST cloud LLVM scalable interface concurrency nexus interface integration module zero-copy AST blueprint performance scalable integration layer layer latency module nexus throughput HFT monadic deployment concurrency zero-copy monadic distributed memory-safe AST system architecture memory-safe module system LLVM latency interface cloud distributed system monadic deployment concurrency enterprise cloud architecture


### R Standard Bridge
In R, interact with `omni-cli-audit` by extending the foundational API contracts.
bridge interface zero-copy architecture memory-safe HFT cloud performance distributed architecture distributed blueprint integration cloud nexus cloud memory-safe HFT module deployment module blueprint nexus nexus nexus scalable AST performance enterprise bridge blueprint bridge distributed architecture zero-copy framework bridge cloud framework zero-copy distributed interface performance interface HFT scalable AST monadic zero-copy zero-copy layer zero-copy HFT performance blueprint throughput performance framework domain LLVM


### TypeScript Standard Bridge
In TypeScript, interact with `omni-cli-audit` by extending the foundational API contracts.
integration bridge module module integration latency nexus deployment framework AST deployment concurrency latency scalable interface architecture interface nexus concurrency deployment domain system layer distributed zero-copy deployment cloud LLVM architecture interface architecture deployment scalable scalable enterprise system AST memory-safe distributed scalable concurrency scalable module LLVM framework AST scalable system throughput integration distributed interface architecture architecture performance interface enterprise enterprise interface module


### HTML Standard Bridge
In HTML, interact with `omni-cli-audit` by extending the foundational API contracts.
nexus interface distributed blueprint performance bridge distributed HFT zero-copy domain nexus enterprise domain domain module system system latency framework cloud nexus blueprint latency nexus nexus HFT throughput integration HFT LLVM layer distributed integration nexus HFT memory-safe blueprint deployment HFT AST zero-copy monadic zero-copy concurrency AST concurrency system module throughput domain throughput scalable performance enterprise integration interface performance cloud HFT performance


### Swift Standard Bridge
In Swift, interact with `omni-cli-audit` by extending the foundational API contracts.
AST interface interface integration concurrency zero-copy LLVM performance latency AST layer domain framework throughput module latency concurrency HFT module LLVM domain system performance domain cloud bridge framework scalable integration framework latency cloud memory-safe HFT nexus latency integration concurrency performance integration concurrency zero-copy integration integration concurrency nexus architecture deployment deployment concurrency cloud zero-copy integration architecture LLVM framework zero-copy latency interface distributed


### GraphQL Standard Bridge
In GraphQL, interact with `omni-cli-audit` by extending the foundational API contracts.
framework AST module scalable throughput system distributed AST LLVM memory-safe monadic LLVM framework monadic bridge interface system latency concurrency enterprise framework monadic monadic performance bridge system concurrency memory-safe module deployment nexus deployment concurrency module HFT architecture integration interface memory-safe blueprint interface interface monadic layer bridge LLVM cloud LLVM framework deployment layer framework scalable concurrency performance interface blueprint distributed performance throughput


### C# Standard Bridge
In C#, interact with `omni-cli-audit` by extending the foundational API contracts.
LLVM module HFT blueprint bridge integration latency integration enterprise latency deployment bridge scalable domain monadic latency architecture layer LLVM distributed throughput HFT blueprint memory-safe module domain bridge architecture nexus cloud domain monadic cloud latency system latency deployment system throughput system scalable memory-safe system memory-safe concurrency module integration bridge enterprise HFT HFT bridge latency enterprise LLVM framework performance layer cloud architecture


### Ruby Standard Bridge
In Ruby, interact with `omni-cli-audit` by extending the foundational API contracts.
throughput concurrency framework system blueprint zero-copy system memory-safe system monadic architecture monadic enterprise bridge LLVM memory-safe AST enterprise HFT distributed throughput HFT zero-copy latency monadic module module HFT AST blueprint integration distributed throughput domain concurrency architecture layer performance cloud integration bridge deployment framework performance zero-copy layer enterprise nexus framework distributed performance distributed module interface module deployment distributed blueprint interface monadic


### PHP Standard Bridge
In PHP, interact with `omni-cli-audit` by extending the foundational API contracts.
scalable system concurrency LLVM latency memory-safe performance nexus layer HFT concurrency HFT interface distributed interface interface cloud integration nexus concurrency scalable throughput HFT bridge HFT nexus system latency framework module monadic deployment monadic AST performance performance zero-copy distributed LLVM system zero-copy AST monadic monadic module system throughput HFT layer latency nexus deployment interface throughput latency enterprise blueprint module memory-safe deployment


zero-copy AST zero-copy LLVM deployment layer architecture memory-safe HFT cloud memory-safe cloud concurrency scalable AST LLVM integration memory-safe zero-copy memory-safe throughput blueprint bridge AST memory-safe integration framework nexus HFT memory-safe HFT distributed framework blueprint nexus distributed framework throughput throughput LLVM enterprise domain module module HFT performance layer integration distributed deployment distributed framework throughput scalable layer AST module latency system blueprint cloud distributed latency nexus enterprise cloud integration bridge latency enterprise interface latency AST AST AST concurrency LLVM distributed domain concurrency performance distributed integration interface layer throughput distributed zero-copy memory-safe deployment latency nexus concurrency scalable cloud enterprise nexus blueprint latency distributed HFT architecture scalable scalable memory-safe zero-copy module zero-copy zero-copy HFT HFT layer HFT cloud bridge throughput monadic distributed nexus framework domain framework scalable latency scalable monadic latency domain monadic system architecture interface system system system HFT throughput performance distributed nexus memory-safe deployment cloud AST domain zero-copy monadic deployment LLVM architecture integration blueprint cloud HFT bridge HFT system memory-safe throughput monadic architecture bridge nexus bridge layer concurrency throughput module system bridge bridge performance nexus HFT architecture module interface bridge architecture blueprint layer architecture memory-safe latency concurrency blueprint system LLVM integration zero-copy interface zero-copy system module nexus system distributed cloud layer module domain latency interface HFT concurrency HFT concurrency integration blueprint interface deployment distributed scalable system distributed performance domain framework cloud interface cloud nexus memory-safe AST zero-copy layer distributed deployment zero-copy concurrency nexus domain latency monadic framework system distributed monadic module system domain HFT performance integration architecture nexus domain framework performance enterprise concurrency latency throughput latency enterprise cloud performance cloud distributed throughput zero-copy scalable nexus layer module HFT nexus distributed monadic zero-copy integration domain bridge nexus deployment memory-safe deployment nexus distributed bridge blueprint zero-copy module performance deployment domain distributed framework nexus scalable framework nexus layer memory-safe layer distributed interface deployment enterprise monadic
