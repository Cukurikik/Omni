# OMNI Framework — Deployment Guide

> Panduan lengkap deployment OMNI Framework ke berbagai environment.

---

## 1. Local Development

### Start All Services

```bash
# Terminal 1: Go API Gateway
cd api
go run main.go
# Server running on http://localhost:8080

# Terminal 2: UI Dashboard
cd ui
npm run dev
# Dashboard on http://localhost:5173

# Terminal 3: Run OMNI programs
omni run examples/hello.omni
```

### Environment Variables

Buat file `.env` di root project:

```env
# Server
PORT=8080
HOST=0.0.0.0
ENV=development

# Database
DATABASE_URL=postgresql://localhost:5432/omni
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET=your-secret-key
API_KEY=your-api-key

# OMNI Cloud
OMNI_CLOUD_REGION=id-jkt-1
OMNI_CLOUD_TOKEN=your-cloud-token
```

---

## 2. Production — Unikernel (Recommended)

OMNI dapat dikompilasi menjadi unikernel berukuran 3-8MB dengan cold start <10ms.

```bash
# Build unikernel
omni unikernel build --target cloud --optimize release

# Output: app.ukl (3-8MB)

# Deploy ke OMNI Cloud
omni cloud deploy app.ukl \
  --region id-jkt-1 \
  --replicas 3 \
  --memory 256mb \
  --cpu 0.5
```

---

## 3. Docker

### Dockerfile

```dockerfile
# Stage 1: Build Go API
FROM golang:1.24-alpine AS builder
WORKDIR /app
COPY api/ ./api/
COPY go.work go.work.sum ./
RUN cd api && CGO_ENABLED=0 go build -ldflags="-w -s" -o /omni-gateway

# Stage 2: Runtime
FROM alpine:3.19
RUN apk add --no-cache ca-certificates
COPY --from=builder /omni-gateway /usr/local/bin/
COPY release/public/ /app/public/
EXPOSE 8080
CMD ["omni-gateway"]
```

### Docker Compose

```yaml
version: '3.9'
services:
  omni-gateway:
    build: .
    ports:
      - "8080:8080"
    environment:
      - ENV=production
      - DATABASE_URL=postgresql://db:5432/omni
    depends_on:
      - db
      - redis

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: omni
      POSTGRES_PASSWORD: secure-password
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

---

## 4. VPS / Bare Metal

```bash
# Build binary
cd api
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 \
  go build -ldflags="-w -s" -o omni-gateway main.go

# Transfer ke server
scp omni-gateway user@server:/opt/omni/

# Setup systemd service
sudo tee /etc/systemd/system/omni.service << EOF
[Unit]
Description=OMNI Framework Gateway
After=network.target

[Service]
Type=simple
User=omni
ExecStart=/opt/omni/omni-gateway
Restart=always
RestartSec=5
Environment=ENV=production
Environment=PORT=8080

[Install]
WantedBy=multi-user.target
EOF

# Enable dan start
sudo systemctl enable omni
sudo systemctl start omni
```

---

## 5. CI/CD Pipeline

OMNI menggunakan GitHub Actions untuk CI/CD. Workflow ada di `.github/workflows/ci-cd.yml`.

### Pipeline Stages

```
Push to main → Validate Go → Build → Deploy
```

### Setup Secrets

Tambahkan secrets berikut di GitHub Repository Settings:

| Secret | Deskripsi |
|--------|-----------|
| `VPS_IP` | IP address server produksi |
| `VPS_USER` | SSH username |
| `SSH_PRIVATE_KEY` | SSH private key untuk deployment |

---

## 6. Monitoring

### Health Check

```bash
curl http://localhost:8080/api/health
# {"status": "ok", "version": "2.0.0", "uptime": "24h30m"}
```

### Logs

```bash
# Local
omni cloud logs --follow

# Docker
docker logs -f omni-gateway

# Systemd
journalctl -u omni -f
```

---

*Untuk pertanyaan deployment, buka [Discussion](https://github.com/Cukurikik/Omni/discussions) di GitHub.*
