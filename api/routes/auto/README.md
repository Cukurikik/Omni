# 🛣️ OMNI-ROUTER: Auto API Routes

File `.go` di folder ini akan otomatis terdaftar sebagai API endpoint
oleh CLI saat menjalankan `omni dev` atau `omni build`.

## Cara Pakai

1. Buat file baru, misal: `users.go`
2. Package HARUS `routes` (bukan `auto`)
3. Define handler function dengan nama `UsersHandler`
4. Jalankan `omni dev`
5. URL aktif: `GET /api/auto/users` ✅

## Contoh File

```go
package routes

import "net/http"

func UsersHandler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "application/json")
    w.Write([]byte(`{"users": ["alice", "bob"]}`))
}
```

## Convention

| File | Handler Function | URL |
|------|-----------------|-----|
| `users.go` | `UsersHandler` | `/api/auto/users` |
| `payment_history.go` | `PaymentHistoryHandler` | `/api/auto/payment-history` |
| `health_check.go` | `HealthCheckHandler` | `/api/auto/health-check` |
