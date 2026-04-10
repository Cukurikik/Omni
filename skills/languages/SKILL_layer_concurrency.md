# SKILL: CONCURRENCY LAYER — Go, JavaScript
**File:** `languages/SKILL_layer_concurrency.md`  
**Layer:** Languages  
**Bahasa:** Golang · JavaScript

---

## Peran Domain

Concurrency Layer menangani semua I/O asinkron, jaringan, dan paralelisme berbasis message-passing. Layer ini tidak pernah menyentuh memori secara manual.

| Bahasa | Keunggulan | Kapan Digunakan |
|--------|-----------|-----------------|
| **Golang** | Green threads, channel CSP, HTTP/3, low latency | Microservice, API gateway, background worker |
| **JavaScript** | Event loop, WebSocket, browser runtime, streaming | Real-time UI update, webhook handler, SSE |

---

## Golang — Idiom OMNI

```omni
// HTTP/3 server dengan goroutine pool
service ApiGateway {
  fn start(addr: string) -> Result<(), NetworkError> {
    let router = go::http3::Router::new()
    router.get("/health", handle_health)
    router.post("/payments", handle_payment)
    go::http3::serve(addr, router)
  }
}

// Channel-based worker pool
fn spawn_worker_pool(n: int) -> go::Channel<WorkItem> {
  let (tx, rx) = go::channel::<WorkItem>(buffer: 1000)

  for _ in 0..n {
    go spawn {
      for item in rx {
        let result = process_item(item)
        match result {
          Ok(v)  => emit("worker.done", v),
          Err(e) => emit("worker.error", e),
        }
      }
    }
  }
  tx
}
```

---

## JavaScript — Idiom OMNI

```omni
// Event loop untuk real-time data streaming
async evloop fn stream_market_data(
  symbol: string,
  on_tick: fn(Tick) -> ()
) -> Result<(), StreamError> {
  let ws = await js::WebSocket::connect("wss://feed.exchange.com")

  ws.on("message", |raw| {
    let tick = Tick::parse(raw)?
    on_tick(tick)
  })

  ws.on("error", |e| {
    emit("stream.error", e)
  })

  await ws.keep_alive()
}
```

---

## Pola Komunikasi Antar Layer

```omni
// Go menerima request dari domain layer dan mengirim ke compute layer
// JANGAN proses bisnis di sini — hanya routing!

service OrderRouter {
  fn route_order(order: Order) -> Result<(), RouterError> {
    match order.type {
      OrderType::Limit  => go spawn compute::run_limit_algo(order),
      OrderType::Market => go spawn compute::run_market_algo(order),
      OrderType::Stop   => go spawn compute::run_stop_algo(order),
    }
    Ok(())
  }
}
```

---

## Aturan Concurrency Layer

1. Goroutine HARUS selalu memiliki exit condition — jangan buat goroutine yang tidak bisa dihentikan
2. Channel buffer size HARUS didefinisikan eksplisit — jangan unbuffered kecuali memang sinkronisasi
3. JavaScript event loop DILARANG memblokir — jangan ada operasi CPU-intensive di sini
4. Semua error dari goroutine HARUS di-emit ke event bus — jangan dibiarkan hilang diam-diam

---

*ANTIGRAVITY Skills — languages/SKILL_layer_concurrency.md*
