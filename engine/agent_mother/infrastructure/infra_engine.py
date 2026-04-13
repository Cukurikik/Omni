import time
import uuid
import random
import json
import math
from enum import Enum
from collections import defaultdict

# ==========================================
# 🏗️ AGENT MOTHER: Feature Store + Colab Enterprise + Workbench
# ==========================================
#
# PROSES BELAJAR JUJUR:
# ────────────────────────────────────────────────
#
# 1. FEATURE STORE — Penyimpanan fitur yang konsisten
#    ┌──────────────────────────────────────────────────┐
#    │ MASALAH TANPA FEATURE STORE:                      │
#    │ - Training pakai fitur versi A                    │
#    │ - Serving pakai fitur versi B                     │
#    │ - Train-serve SKEW → model deploy tapi buruk!     │
#    │                                                    │
#    │ VERTEX AI FEATURE STORE:                           │
#    │ - FeatureGroup: kumpulan fitur terkait            │
#    │ - Feature: satu kolom data (age, revenue, etc.)   │
#    │ - FeatureView: materialized view untuk serving    │
#    │ - Online Store: real-time serving (low latency)   │
#    │ - Offline Store: batch serving (BigQuery)         │
#    │                                                    │
#    │ UNTUK AGENT:                                       │
#    │ - User features: preference, history, tier        │
#    │ - Context features: time, location, device       │
#    │ - Agent state features: session count, tools used │
#    │ → Agent ambil fitur real-time untuk personalisasi │
#    └──────────────────────────────────────────────────┘
#
# 2. COLAB ENTERPRISE — Managed Jupyter untuk agent dev
#    ┌──────────────────────────────────────────────────┐
#    │ COLAB ENTERPRISE (bukan Colab biasa!):             │
#    │ - Managed JupyterLab di VPC                       │
#    │ - GPU/TPU runtimes (A100, T4)                     │
#    │ - Collaborative real-time editing                 │
#    │ - BigQuery + GCS integration native               │
#    │ - Version control built-in                        │
#    │ - Scheduled execution (notebook as pipeline)      │
#    │                                                    │
#    │ UNTUK AGENT:                                       │
#    │ - Iterasi cepat: test prompt + tool calling       │
#    │ - Data exploration untuk RAG knowledge base       │
#    │ - Fine-tuning experiments (train + eval loop)     │
#    │ - Notebook → pipeline → production deployment     │
#    └──────────────────────────────────────────────────┘
#
# 3. WORKBENCH — Full ML development environment
#    ┌──────────────────────────────────────────────────┐
#    │ VERTEX AI WORKBENCH:                               │
#    │ - Managed Notebooks (JupyterLab instances)        │
#    │ - Pre-installed: TF, PyTorch, JAX, Vertex SDK     │
#    │ - Custom containers (bring your own image)        │
#    │ - GPU attachment (dynamic, pay per use)            │
#    │ - Idle shutdown (cost saving)                      │
#    │ - Git integration                                 │
#    │                                                    │
#    │ BEDA vs COLAB ENTERPRISE:                          │
#    │ - Workbench: full control, persistent, custom env │
#    │ - Colab: quick iteration, temporary, collaborative│
#    └──────────────────────────────────────────────────┘

# ─────────────────────────────────────────────────
# KOMPONEN 1: Feature Store
# ─────────────────────────────────────────────────
class Feature:
    """Single feature definition."""
    def __init__(self, name, dtype="FLOAT", description=""):
        self.name = name
        self.dtype = dtype
        self.description = description


class FeatureGroup:
    """Group of related features (like a table)."""
    def __init__(self, name, entity_id_column="entity_id"):
        self.group_id = str(uuid.uuid4())[:8]
        self.name = name
        self.entity_id_column = entity_id_column
        self.features = {}
        self.data = {}  # entity_id → {feature_name: value}

    def add_feature(self, feature):
        self.features[feature.name] = feature

    def ingest(self, records):
        """Ingest feature values."""
        for record in records:
            entity_id = record[self.entity_id_column]
            if entity_id not in self.data:
                self.data[entity_id] = {}
            for k, v in record.items():
                if k != self.entity_id_column and k in self.features:
                    self.data[entity_id][k] = v

    def get_features(self, entity_id, feature_names=None):
        """Online serving: get features by entity ID (low latency)."""
        row = self.data.get(entity_id, {})
        if feature_names:
            return {k: row.get(k) for k in feature_names}
        return row


class OnlineStore:
    """
    PELAJARAN: Online Store = real-time feature serving.
    Latency requirement: < 10ms.
    Powered by Bigtable internally.
    """
    def __init__(self, name):
        self.name = name
        self.feature_groups = {}
        self.serving_log = []

    def register_group(self, group):
        self.feature_groups[group.name] = group

    def serve(self, group_name, entity_id, feature_names=None):
        """Serve features in real-time."""
        group = self.feature_groups.get(group_name)
        if not group:
            return {"error": f"Group '{group_name}' not found"}

        start = time.time()
        features = group.get_features(entity_id, feature_names)
        latency_ms = (time.time() - start) * 1000

        result = {
            "entity_id": entity_id,
            "features": features,
            "latency_ms": round(latency_ms, 2),
            "source": "online_store",
        }
        self.serving_log.append(result)
        return result


class FeatureView:
    """Materialized view for batch or online serving."""
    def __init__(self, name, feature_group, selected_features=None):
        self.name = name
        self.feature_group = feature_group
        self.selected_features = selected_features or list(feature_group.features.keys())

    def materialize(self):
        """Create materialized snapshot."""
        rows = []
        for entity_id, features in self.feature_group.data.items():
            row = {"entity_id": entity_id}
            for f in self.selected_features:
                row[f] = features.get(f)
            rows.append(row)
        return rows


# ─────────────────────────────────────────────────
# KOMPONEN 2: Colab Enterprise
# ─────────────────────────────────────────────────
class ColabEnterprise:
    """
    PELAJARAN: Colab Enterprise = managed Jupyter dalam VPC.
    - GPU runtimes (T4, A100)
    - Team collaboration
    - Scheduled execution
    - Native BigQuery/GCS
    """
    def __init__(self, project_id="my-project"):
        self.project_id = project_id
        self.runtimes = {}
        self.notebooks = {}
        self.schedules = []

    def create_runtime(self, name, machine_type="n1-standard-4", accelerator=None):
        runtime = {
            "id": str(uuid.uuid4())[:8],
            "name": name,
            "machine_type": machine_type,
            "accelerator": accelerator,
            "status": "RUNNING",
            "created_at": time.time(),
        }
        self.runtimes[name] = runtime
        print(f"      🖥️  Runtime '{name}': {machine_type}" +
              (f" + {accelerator}" if accelerator else ""))
        return runtime

    def create_notebook(self, name, runtime_name, cells=None):
        notebook = {
            "id": str(uuid.uuid4())[:8],
            "name": name,
            "runtime": runtime_name,
            "cells": cells or [],
            "status": "IDLE",
            "version": 1,
        }
        self.notebooks[name] = notebook
        return notebook

    def execute_notebook(self, name):
        """Execute notebook (simulate)."""
        nb = self.notebooks[name]
        nb["status"] = "EXECUTING"
        results = []
        for i, cell in enumerate(nb["cells"]):
            result = f"Output of cell {i+1}: {cell[:30]}..."
            results.append(result)
        nb["status"] = "COMPLETED"
        nb["last_run"] = time.time()
        return results

    def schedule_notebook(self, name, cron="0 */6 * * *"):
        schedule = {
            "notebook": name,
            "cron": cron,
            "enabled": True,
            "next_run": "in 6 hours",
        }
        self.schedules.append(schedule)
        print(f"      ⏰ Scheduled '{name}': {cron}")
        return schedule


# ─────────────────────────────────────────────────
# KOMPONEN 3: Workbench
# ─────────────────────────────────────────────────
class Workbench:
    """
    PELAJARAN: Workbench = persistent ML environment.
    Beda dari Colab: lebih powerful, persistent, custom containers.
    """
    def __init__(self):
        self.instances = {}

    def create_instance(self, name, machine_type="n1-standard-8",
                        accelerator="NVIDIA_TESLA_T4", idle_shutdown_minutes=60,
                        container_image=None):
        instance = {
            "id": str(uuid.uuid4())[:8],
            "name": name,
            "machine_type": machine_type,
            "accelerator": accelerator,
            "idle_shutdown_minutes": idle_shutdown_minutes,
            "container_image": container_image or "gcr.io/deeplearning-platform-release/pytorch-gpu",
            "status": "ACTIVE",
            "pre_installed": ["tensorflow", "pytorch", "jax", "vertex-ai-sdk", "langchain", "llamaindex"],
            "disk_gb": 200,
            "created_at": time.time(),
        }
        self.instances[name] = instance
        print(f"      🔧 Workbench '{name}': {machine_type} + {accelerator}")
        print(f"         Container: {instance['container_image']}")
        print(f"         Pre-installed: {', '.join(instance['pre_installed'][:4])}...")
        print(f"         Idle shutdown: {idle_shutdown_minutes} min")
        return instance

    def attach_gpu(self, instance_name, gpu_type="NVIDIA_A100"):
        inst = self.instances[instance_name]
        inst["accelerator"] = gpu_type
        print(f"      🎮 GPU attached: {gpu_type} → {instance_name}")

    def list_instances(self):
        return [{
            "name": i["name"],
            "status": i["status"],
            "machine": i["machine_type"],
            "gpu": i["accelerator"],
        } for i in self.instances.values()]


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("🏗️ AGENT MOTHER: Feature Store + Colab Enterprise + Workbench")
    print("=" * 70)
    print()
    print("📖 PROSES PEMBELAJARAN:")
    print("   Feature Store: FeatureGroup → OnlineStore (realtime) + OfflineStore (batch)")
    print("   Colab Enterprise: managed Jupyter + GPU + scheduling + collaboration")
    print("   Workbench: persistent ML env + custom container + GPU dynamic attach")

    # ── PART 1: Feature Store ──
    print(f"\n{'─'*60}")
    print("📋 PART 1: Feature Store (Online + Offline)")

    # Create feature group
    user_features = FeatureGroup("user_profile", entity_id_column="user_id")
    user_features.add_feature(Feature("loyalty_tier", "STRING", "Gold/Silver/Bronze"))
    user_features.add_feature(Feature("total_orders", "INT", "Total order count"))
    user_features.add_feature(Feature("avg_order_value", "FLOAT", "Average order value"))
    user_features.add_feature(Feature("preferred_language", "STRING", "User language"))
    user_features.add_feature(Feature("last_interaction_days", "INT", "Days since last chat"))

    # Ingest data
    user_features.ingest([
        {"user_id": "U001", "loyalty_tier": "Gold", "total_orders": 42, "avg_order_value": 156.30, "preferred_language": "id", "last_interaction_days": 2},
        {"user_id": "U002", "loyalty_tier": "Silver", "total_orders": 8, "avg_order_value": 45.00, "preferred_language": "en", "last_interaction_days": 15},
        {"user_id": "U003", "loyalty_tier": "Bronze", "total_orders": 1, "avg_order_value": 25.00, "preferred_language": "id", "last_interaction_days": 90},
    ])
    print(f"   Feature Group '{user_features.name}': {len(user_features.features)} features, {len(user_features.data)} entities")

    # Online serving
    online = OnlineStore("agent_online_store")
    online.register_group(user_features)

    print("\n   🚀 Online Serving (real-time):")
    for uid in ["U001", "U002", "U003"]:
        result = online.serve("user_profile", uid, ["loyalty_tier", "avg_order_value"])
        print(f"      {uid}: {result['features']} (latency: {result['latency_ms']:.2f}ms)")

    # Feature view
    view = FeatureView("agent_view", user_features, ["loyalty_tier", "total_orders"])
    materialized = view.materialize()
    print(f"\n   📊 Feature View '{view.name}': {len(materialized)} rows")
    for row in materialized:
        print(f"      {row}")

    # Agent using features for personalization
    print(f"\n   🤖 Agent Personalization Example:")
    user_features_result = online.serve("user_profile", "U001")
    features = user_features_result["features"]
    print(f"      User U001: tier={features['loyalty_tier']}, orders={features['total_orders']}")
    print(f"      → Agent: 'Selamat datang kembali, pelanggan Gold! Terima kasih atas 42 pesanan Anda.'")
    print(f"      (personalized greeting based on feature store data)")

    # ── PART 2: Colab Enterprise ──
    print(f"\n{'─'*60}")
    print("📋 PART 2: Colab Enterprise")
    colab = ColabEnterprise("omni-project-123")

    colab.create_runtime("agent-dev", "n1-standard-8", "NVIDIA_TESLA_T4")
    colab.create_runtime("fine-tune-gpu", "a2-highgpu-1g", "NVIDIA_A100")

    nb = colab.create_notebook("agent_experiment", "agent-dev", cells=[
        "from vertexai import agent_builder",
        "agent = agent_builder.create(model='gemini-2.0-flash')",
        "result = agent.run('Apa itu RAG?')",
        "print(result)",
    ])
    results = colab.execute_notebook("agent_experiment")
    print(f"   📓 Notebook executed: {len(results)} cells")
    for r in results:
        print(f"      {r}")

    colab.schedule_notebook("agent_experiment", "0 */6 * * *")

    # ── PART 3: Workbench ──
    print(f"\n{'─'*60}")
    print("📋 PART 3: Workbench (Persistent ML Environment)")
    wb = Workbench()

    wb.create_instance("agent-workbench", "n1-standard-16", "NVIDIA_TESLA_T4",
                       idle_shutdown_minutes=120)

    wb.create_instance("fine-tune-station", "a2-highgpu-1g", "NVIDIA_A100",
                       idle_shutdown_minutes=60,
                       container_image="gcr.io/my-project/custom-agent-env:latest")

    print(f"\n   📋 All Instances:")
    for inst in wb.list_instances():
        print(f"      {inst['name']}: {inst['machine']} + {inst['gpu']} ({inst['status']})")

    # Dynamic GPU upgrade
    wb.attach_gpu("agent-workbench", "NVIDIA_H100")

    # ── Comparison Table ──
    print(f"\n{'─'*60}")
    print("📋 COMPARISON: Colab Enterprise vs Workbench")
    print("   ┌────────────────────┬──────────────────┬──────────────────┐")
    print("   │ Feature            │ Colab Enterprise │ Workbench        │")
    print("   ├────────────────────┼──────────────────┼──────────────────┤")
    print("   │ Persistence        │ Temporary        │ Persistent       │")
    print("   │ Collaboration      │ Real-time        │ Git-based        │")
    print("   │ Custom Container   │ Limited          │ Full control     │")
    print("   │ GPU Options        │ T4, A100         │ T4, A100, H100   │")
    print("   │ Scheduling         │ Built-in         │ Via Pipelines    │")
    print("   │ Cost               │ Pay-per-use      │ Pay while running│")
    print("   │ Best For           │ Quick iteration  │ Heavy development│")
    print("   └────────────────────┴──────────────────┴──────────────────┘")

    print(f"\n{'='*70}")
    print("✅ Feature Store + Colab Enterprise + Workbench: DIPELAJARI.")
    print("   Feature Store: FeatureGroup + OnlineStore (real-time) ✓")
    print("   Feature View: materialized snapshots for serving ✓")
    print("   Agent personalization via Feature Store ✓")
    print("   Colab Enterprise: runtimes + notebooks + scheduling ✓")
    print("   Workbench: persistent instances + custom containers ✓")
    print("   GPU dynamic attachment (T4 → A100 → H100) ✓")
    print(f"{'='*70}")
