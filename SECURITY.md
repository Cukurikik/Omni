# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.0.x   | ✅ Active support |
| 1.x.x   | ❌ No longer supported |

## Reporting a Vulnerability

Keamanan OMNI Framework adalah prioritas utama kami. Jika Anda menemukan kerentanan keamanan, **JANGAN** buat public issue.

### Cara Melaporkan

1. **Email**: Kirim laporan ke **security@omniframework.dev**
2. **Subject**: `[SECURITY] Brief description of vulnerability`
3. **Sertakan**:
   - Deskripsi kerentanan
   - Langkah reproduksi
   - Dampak potensial
   - Saran perbaikan (jika ada)

### Response Timeline

| Tahap | Waktu |
|-------|-------|
| Acknowledgement | 24 jam |
| Initial Assessment | 72 jam |
| Fix Development | 7-14 hari |
| Public Disclosure | 30 hari setelah fix |

### Scope

Berikut area yang termasuk dalam scope security:

- **OMNI Runtime Engine** — Memory safety, sandboxing, permission model
- **OMNI-NEXUS Registry** — Package integrity, supply chain security
- **Go API Gateway** — Authentication, authorization, injection attacks
- **OMNI Cloud PaaS** — Container isolation, data encryption
- **Cryptographic modules** — Key management, encryption implementations

### Out of Scope

- Denial of Service (DoS) melalui resource exhaustion pada demo instances
- Social engineering terhadap anggota tim
- Kerentanan pada dependensi third-party yang sudah dilaporkan

### Bug Bounty

Saat ini kami belum memiliki program bug bounty formal, tetapi kontributor yang melaporkan kerentanan kritis akan mendapatkan:

- Credit di SECURITY.md dan CHANGELOG
- Akses gratis ke OMNI Pro tier selama 1 tahun
- Swag eksklusif OMNI Framework

### Permission Model

OMNI Framework menggunakan permission model eksplisit di `Omnifile.toml`:

```toml
[permissions]
allow_net    = ["api.stripe.com"]   # Whitelist — bukan wildcard
allow_fs     = ["/tmp/myapp/"]      # Restricted filesystem access
allow_env    = ["API_KEY"]          # Explicit env vars only
allow_thread = true                  # Concurrency permission
```

Kode yang tidak mendeklarasikan permission akan **ditolak saat runtime**.

---

*Terima kasih telah membantu menjaga keamanan OMNI Framework.*
