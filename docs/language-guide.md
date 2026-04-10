# OMNI Language Guide

> Panduan lengkap bahasa pemrograman OMNI (`.omni`)

---

## 1. Pendahuluan

Bahasa OMNI adalah bahasa pemrograman native dari OMNI Framework. Ia menggabungkan syntax terbaik dari Rust (safety), TypeScript (types), dan Go (concurrency) menjadi satu bahasa yang kohesif.

**File extension:** `.omni`  
**Paradigma:** Multi-paradigm (functional, imperative, concurrent)  
**Type system:** Static, strong, inferred  
**Memory model:** Ownership-based (inspired by Rust)

---

## 2. Syntax Dasar

### 2.1 Variabel & Konstanta

```omni
// Immutable by default
val name: String = "OMNI"
val count = 42                    // Type inference

// Mutable — harus eksplisit
mutable var counter: i64 = 0
counter += 1

// Konstanta compile-time
const MAX_CONNECTIONS: u32 = 10_000
```

### 2.2 Fungsi

```omni
// Fungsi dasar
fn add(a: i32, b: i32) -> i32 {
    a + b   // implicit return (ekspresi terakhir)
}

// Fungsi dengan error handling
fn divide(a: f64, b: f64) -> Result<f64, MathError> {
    guard b != 0.0 else {
        return Err(MathError::DivisionByZero)
    }
    Ok(a / b)
}

// Async function
async fn fetch_data(url: String) -> Result<Data, NetError> {
    let response = http::get(url).await?
    let data = response.json::<Data>().await?
    Ok(data)
}

// Generic function
fn first<T>(items: Vec<T>) -> Option<T> {
    if items.is_empty() { None }
    else { Some(items[0]) }
}
```

### 2.3 Struct & Enum

```omni
// Struct
struct User {
    id: UUID,
    name: String,
    email: String,
    role: Role,
    created_at: DateTime,
}

// Enum (algebraic data types)
enum Role {
    Admin,
    Editor { permissions: Vec<String> },
    Viewer,
}

// Pattern matching
fn describe_role(role: Role) -> String {
    match role {
        Role::Admin => "Full access administrator",
        Role::Editor { permissions } => format!("Editor with {} permissions", permissions.len()),
        Role::Viewer => "Read-only viewer",
    }
}
```

### 2.4 Traits & Interfaces

```omni
// Trait (like Rust traits / TypeScript interfaces)
trait Serializable {
    fn serialize(&self) -> Vec<u8>
    fn deserialize(data: &[u8]) -> Result<Self, SerError>
}

// Implementation
impl Serializable for User {
    fn serialize(&self) -> Vec<u8> {
        json::to_bytes(self)
    }
    
    fn deserialize(data: &[u8]) -> Result<User, SerError> {
        json::from_bytes::<User>(data)
    }
}
```

### 2.5 Concurrency

```omni
// Spawn goroutine (Go-style)
spawn async {
    let result = heavy_computation().await
    println("Done: {}", result)
}

// Channels (CSP model)
let (tx, rx) = channel::<Message>()

spawn async {
    tx.send(Message::Data(payload)).await
}

// Receive
let msg = rx.recv().await?

// Select (multiplexing)
select {
    msg from rx1 => handle_a(msg),
    msg from rx2 => handle_b(msg),
    after 5.seconds() => timeout(),
}
```

### 2.6 Modules & Imports

```omni
// Declare module
module my_app::auth

// Import
use omni_std::collections::{HashMap, Vec}
use omni_net::http::{Server, Router}
use @system/crypto::{AES256}        // Cross-language import
use @compute/ml::{Classifier}       // From compute layer

// Re-export
pub use crate::auth::middleware::*
```

---

## 3. Cross-Language Interop

### 3.1 Language Annotations

```omni
// Rust block
@rust
fn memory_safe_parse(input: &str) -> Result<AST, ParseError> {
    let tokens = Lexer::new(input).tokenize()?
    Parser::new(tokens).parse()
}

// Go block
@go
func HandleRequest(w http.ResponseWriter, r *http.Request) {
    data := omni_bridge::memory_safe_parse(r.Body)
    json.NewEncoder(w).Encode(data)
}

// Python block
@python
def train_model(data: List[float]) -> Model:
    import tensorflow as tf
    model = tf.keras.Sequential([...])
    model.fit(data)
    return model

// TypeScript block  
@typescript
interface APIResponse<T> {
    data: T;
    status: number;
    timestamp: Date;
}
```

### 3.2 OMNI Bridge Protocol

```omni
// Memanggil fungsi dari layer lain melalui bridge
use @omni-bridge/system/crypto as crypto
use @omni-bridge/compute/ml as ml
use @omni-bridge/domain/payment as payment

fn process_secure_payment(req: PaymentRequest) -> Result<Receipt, Error> {
    let encrypted = crypto::encrypt(req.card_data)?    // System layer
    let risk = ml::assess_fraud_risk(req)?              // Compute layer
    let receipt = payment::charge(encrypted, risk)?     // Domain layer
    Ok(receipt)
}
```

---

## 4. Error Handling

```omni
// Custom error type
enum AppError {
    NotFound(String),
    Unauthorized,
    DatabaseError(DbError),
    ValidationError { field: String, message: String },
}

// Operator ? untuk propagasi
fn get_user(id: UUID) -> Result<User, AppError> {
    let conn = db::connect()?                           // propagate DbError
    let row = conn.query("SELECT * FROM users WHERE id = $1", &[id])?
    let user = User::from_row(row)?
    Ok(user)
}

// map_err untuk konversi error
fn api_get_user(id: String) -> Result<User, AppError> {
    let uuid = UUID::parse(id).map_err(|_| AppError::ValidationError {
        field: "id".into(),
        message: "Invalid UUID format".into(),
    })?
    get_user(uuid)
}
```

---

## 5. Testing

```omni
#[test]
module tests {
    use super::*
    
    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5)
        assert_eq!(add(-1, 1), 0)
    }
    
    #[test]
    fn test_divide_by_zero() {
        let result = divide(10.0, 0.0)
        assert!(result.is_err())
        assert_eq!(result.unwrap_err(), MathError::DivisionByZero)
    }
    
    #[test]
    async fn test_fetch_data() {
        let data = fetch_data("https://api.example.com/test").await
        assert!(data.is_ok())
    }
}
```

---

*Untuk contoh program lengkap, lihat `omni-runtime/examples/`*
