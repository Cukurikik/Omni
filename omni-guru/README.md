# Omni-Guru — Universal Technology REST API

Micro-service backend untuk **Omni Mother** yang menguasai seluruh katalog bahasa pemrograman,
tools, simulator, formal verification, dan infrastruktur.

## Arsitektur

```
Omni Mother (UI) ──► Omni-Guru API (FastAPI)
                           │
                    Intent Router (LLM + Function Calling)
                           │
          ┌────────────────┼────────────────┐
          │                │                │
    Code-Engine      Formal-Engine    Sim-Engine
    (Docker/lang)   (Coq/Z3/Dafny)  (gem5/QEMU)
          │                │                │
          └────────────────┴────────────────┘
                           │
                    Object Store (MinIO/S3)
                           │
                    Vector Store (Qdrant)
```

## Endpoints

| Endpoint | Fungsi |
|----------|--------|
| `POST /generate_code` | Generate kode untuk bahasa apapun |
| `POST /run_code` | Compile & run di sandbox Docker |
| `POST /run_simulation` | Hardware/network simulation |
| `POST /verify_formal` | Formal proof (Coq, Z3, Dafny, ...) |
| `POST /apply_infra` | Terraform/Pulumi/Ansible |
| `POST /query_database` | SQL/Graph/TimeSeries query |
| `POST /publish_event` | Kafka/NATS/MQTT messaging |

## Quick Start

### Local (Docker Compose)
```bash
docker-compose up -d
```
API tersedia di `http://localhost:8080`

### Populate Vector Store
```bash
pip install -r requirements.txt
python scripts/populate_vector_store.py
```

### Contoh Request
```bash
# Generate Rust code
curl -X POST http://localhost:8080/generate_code \
  -H "Content-Type: application/json" \
  -d '{"language": "Rust", "description": "Hello World yang membaca nama dari stdin"}'

# Run Python code
curl -X POST http://localhost:8080/run_code \
  -H "Content-Type: application/json" \
  -d '{"language": "python", "source_code": "print(\"Halo dari Omni-Guru!\")"}'

# Verify with Z3
curl -X POST http://localhost:8080/verify_formal \
  -H "Content-Type: application/json" \
  -d '{"tool": "Z3", "source": "(assert (= 1 2))\n(check-sat)"}'
```

## Deploy ke Cloud

### Google Cloud Run
```bash
gcloud run deploy omni-guru \
  --image ghcr.io/yourorg/omni-guru:latest \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --port 8080
```

### AWS Lambda (Container)
```bash
aws ecr create-repository --repository-name omni-guru
docker tag omni-guru:latest <account>.dkr.ecr.<region>.amazonaws.com/omni-guru:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/omni-guru:latest
```

## Environment Variables

| Variable | Default | Keterangan |
|----------|---------|-----------|
| `PORT` | `8080` | Port server |
| `ARTIFACT_BUCKET` | `/tmp/omni-guru-artifacts` | Path artifact storage |
| `MINIO_ENDPOINT` | `minio:9000` | MinIO endpoint |
| `MINIO_ACCESS_KEY` | `minioadmin` | MinIO credentials |
| `MINIO_SECRET_KEY` | `minioadmin` | MinIO secret |
| `OPENAI_API_KEY` | — | Untuk LLM generate_code |
| `QDRANT_URL` | `http://localhost:6333` | Vector store |

## Roadmap

| Milestone | Fokus | Estimasi |
|-----------|-------|----------|
| M0 | FastAPI + Docker sandbox + artifact store | 1 minggu |
| M1 | LLM integration (generate_code, explain) | 1 minggu |
| M2 | Language matrix ≥ 30 bahasa | 2 minggu |
| M3 | Formal verification (Coq, Z3, Dafny, Lean) | 2 minggu |
| M4 | Simulation stack (gem5, QEMU, ns-3) | 3 minggu |
| M5 | Infra & CI/CD (Terraform, Pulumi, Ansible) | 2 minggu |
| M6 | Database & Streaming | 2 minggu |
| M7 | Security & Policy (OPA, Trivy, Bandit) | 1 minggu |
| M8 | Observability (Prometheus, Loki, Jaeger) | 1 minggu |
| M9 | Production hardening | 2 minggu |
| M10 | Multi-region deploy | 1 minggu |

**Total: ~18 minggu untuk coverage ≥ 80% katalog teknologi.**

## Struktur File

```
omni-guru/
├── omni_guru/
│   └── api.py              # FastAPI application utama
├── scripts/
│   └── populate_vector_store.py  # Isi Qdrant dengan katalog
├── catalog.txt             # Seluruh katalog teknologi
├── system_prompt.txt       # System prompt Omni-Guru untuk LLM
├── openapi.yaml            # OpenAPI 3.1 specification
├── Dockerfile              # Container image
├── docker-compose.yml      # Local dev stack (API + MinIO + Qdrant)
├── requirements.txt        # Python dependencies
└── README.md               # Dokumentasi ini
```

## Lisensi
MIT — bebas digunakan dan dimodifikasi.
