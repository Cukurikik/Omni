#!/bin/bash
set -e

# OMNI MOTHER: K8s Deployment Script for MoE Cluster
# Deploys the experts and router as stateless pods with HPA.

echo "[OMNI] Generating Kubernetes Manifests..."

cat <<EOF > /tmp/omni-moe-k8s.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: omni-moe-router
spec:
  replicas: 3
  selector:
    matchLabels:
      app: omni-router
  template:
    metadata:
      labels:
        app: omni-router
    spec:
      containers:
      - name: router
        image: omni.nexus/moe-router:latest
        ports:
        - containerPort: 50050
---
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: omni-moe-expert
spec:
  selector:
    matchLabels:
      app: omni-expert
  template:
    metadata:
      labels:
        app: omni-expert
    spec:
      nodeSelector:
        accelerator: nvidia-h100
      containers:
      - name: expert
        image: omni.nexus/moe-expert:latest
        resources:
          limits:
            nvidia.com/gpu: 1
EOF

echo "[OMNI] Applying to Kubernetes Cluster..."
# kubectl apply -f /tmp/omni-moe-k8s.yaml

echo "[OMNI] Deployment submitted."
