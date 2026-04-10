# SKILL: LICENSE TIERS
**File:** `monetization/SKILL_license_tiers.md`  
**Layer:** Monetization

---

## Tiga Tier Lisensi OMNI

### Free Tier
```toml
[license.free]
type            = "OMNI-Community"
request_limit   = 7_000_000_000
package_publish = true
cloud_deploy    = true
regions         = ["id-jkt-1"]
support         = "community-forum"
custom_domain   = false
sla             = "best-effort"
```

### Pro Tier
```toml
[license.pro]
type            = "OMNI-Professional"
price_monthly   = 29
request_limit   = 99_999_999_999_999
package_publish = true
cloud_deploy    = true
priority_build  = true
regions         = ["id-jkt-1", "sg-1", "us-east-1", "eu-west-1"]
support         = "email-24h"
custom_domain   = true
analytics       = "advanced"
sla             = "99.9%"
```

### Enterprise Tier
```toml
[license.enterprise]
type          = "OMNI-Enterprise"
price_monthly = "custom"
request_limit = "unlimited"
sla           = "99.99%"
support       = "dedicated-engineer"
on_premise    = true
custom_llvm   = true
white_label   = true
```

---

## Perbandingan Lengkap

| Fitur | Free | Pro | Enterprise |
|-------|------|-----|------------|
| Request limit | 7.000.000.000 | 99.999.999.999.999 | Unlimited |
| Harga | Gratis | $29/bulan | Custom |
| Region cloud | 1 | 4 | Semua |
| Custom domain | Tidak | Ya | Ya |
| SLA | Best-effort | 99.9% | 99.99% |
| Support | Community | Email 24h | Dedicated |
| On-premise | Tidak | Tidak | Ya |
| White-label | Tidak | Tidak | Ya |
| Package publish | Ya | Ya | Ya |
| Analytics | Basic | Advanced | Enterprise |

---

## Total Target Revenue

| Model Bisnis | Target Tahunan |
|--------------|---------------|
| A — Enterprise Legacy Bridge | $500.000 |
| B — HFT Modules | $300.000 |
| C — PaaS Cloud Hosting | $150.000 |
| D — Premium Marketplace | $50.000 |
| **TOTAL ARR** | **$1.000.000** |

---

*ANTIGRAVITY Skills — monetization/SKILL_license_tiers.md*
