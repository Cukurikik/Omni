# OMNI Framework — API Reference

> Dokumentasi lengkap API endpoint yang tersedia di OMNI Gateway.

---

## Base URL

```
Development: http://localhost:8080
Production:  https://api.omniframework.dev
```

---

## Authentication

```http
Authorization: Bearer <JWT_TOKEN>
```

---

## Endpoints

### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "version": "2.0.0-OMNI-NEXUS-ULTRA",
  "uptime": "24h30m15s",
  "languages_active": 15,
  "modules_loaded": 22
}
```

---

### OMNI-NEXUS Package Registry

#### List Packages

```http
GET /api/nexus/packages
```

**Response:**
```json
{
  "packages": [
    {
      "name": "omni-std",
      "version": "2.0.0",
      "tier": "core",
      "description": "Standard library for OMNI Framework",
      "downloads": 15420
    }
  ],
  "total": 22
}
```

#### Get Package Detail

```http
GET /api/nexus/packages/:name
```

#### Publish Package

```http
POST /api/nexus/packages
Content-Type: multipart/form-data

manifest: <Omnifile.toml>
archive: <package.tar.gz>
signature: <Ed25519 signature>
```

---

### Code Execution

#### Run OMNI Code

```http
POST /api/execute
Content-Type: application/json

{
  "source": "fn main() { println(\"Hello OMNI!\") }",
  "language": "omni",
  "timeout_ms": 5000
}
```

**Response:**
```json
{
  "output": "Hello OMNI!",
  "exit_code": 0,
  "execution_time_ms": 12,
  "memory_used_bytes": 1048576
}
```

#### Run Polyglot Code

```http
POST /api/execute/polyglot
Content-Type: application/json

{
  "blocks": [
    { "language": "rust", "source": "fn add(a: i32, b: i32) -> i32 { a + b }" },
    { "language": "go", "source": "fmt.Println(omni.Call(\"add\", 2, 3))" }
  ]
}
```

---

### Kinetic Bridge (Native Code)

#### Test Native Bridge

```http
POST /api/kinetic/test
Content-Type: application/json

{
  "operation": "benchmark",
  "iterations": 1000
}
```

---

### Project Management

#### List Projects

```http
GET /api/projects
```

#### Create Project

```http
POST /api/projects
Content-Type: application/json

{
  "name": "my-omni-app",
  "template": "fintech",
  "languages": ["rust", "go", "typescript"]
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "E001",
    "type": "DomainLayerViolation",
    "message": "UI layer cannot directly access System layer memory",
    "suggestion": "Use @omni-bridge/system/memory instead of direct import"
  }
}
```

### Error Codes

| Code | Type | Description |
|------|------|-------------|
| `E001` | `DomainLayerViolation` | Code violates domain layer segregation |
| `E002` | `MissingResultWrapper` | Function must return `Result<T, E>` |
| `E003` | `UnsafeDataCopy` | Data >1MB must use zero-copy transfer |
| `E004` | `PermissionDenied` | Missing permission in Omnifile.toml |
| `E005` | `MissingDocComment` | Public function must have doc comment |
| `E006` | `CompilationError` | Source code failed to compile |
| `E007` | `RuntimeError` | Runtime execution error |
| `E008` | `PackageNotFound` | Package not found in OMNI-NEXUS |
| `E009` | `VersionConflict` | Dependency version conflict |
| `E010` | `Timeout` | Execution exceeded time limit |

---

## Rate Limits

| Tier | Requests/min | Requests/month |
|------|-------------|----------------|
| Community | 60 | 7,000,000,000 |
| Pro | 600 | 99,999,999,999,999 |
| Enterprise | Unlimited | Unlimited |

---

## SDK Usage

### JavaScript/TypeScript

```typescript
import { OmniClient } from '@omni/client';

const client = new OmniClient({
  baseUrl: 'https://api.omniframework.dev',
  apiKey: process.env.OMNI_API_KEY,
});

// Execute code
const result = await client.execute({
  source: 'fn main() { println("Hello!") }',
  language: 'omni',
});

console.log(result.output); // "Hello!"
```

---

*Untuk testing API, gunakan koleksi Postman kami di `docs/postman/`*
