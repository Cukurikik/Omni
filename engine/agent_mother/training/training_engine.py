import time
import uuid
import math
import random
import json
from enum import Enum
from collections import defaultdict

# ==========================================
# 🎓 AGENT MOTHER: Fine Tuning + Training + Experiments + Datasets
# ==========================================
#
# PROSES BELAJAR JUJUR:
# ────────────────────────────────────────────────
#
# 1. FINE TUNING — Melatih ulang LLM agar jago di domain spesifik
#    ┌─────────────────────────────────────────────────┐
#    │ 3 METODE FINE-TUNING:                            │
#    │                                                   │
#    │ a) SUPERVISED FINE-TUNING (SFT)                   │
#    │    Dataset: (input, ideal_output) pairs            │
#    │    Loss: Cross-entropy antara output model vs ideal│
#    │    Cocok: chatbot, Q&A, classification            │
#    │                                                   │
#    │ b) RLHF (Reinforcement Learning from Human)       │
#    │    Dataset: human preference rankings              │
#    │    Train reward model → PPO optimize               │
#    │    Cocok: alignment, safety, tone                  │
#    │                                                   │
#    │ c) LoRA / QLoRA (Parameter-Efficient)              │
#    │    TIDAK update semua parameter (milyaran!).       │
#    │    Hanya train low-rank adapter matrices.          │
#    │    LoRA: ~1% parameters, QLoRA: quantized LoRA    │
#    │    Cocok: limited GPU, cepat, reversible           │
#    │                                                   │
#    │ VERTEX AI FLOW:                                    │
#    │ 1. Upload dataset ke Cloud Storage / BigQuery      │
#    │ 2. Create tuning job (model, dataset, hyperparams) │
#    │ 3. Monitor training (loss curve, eval metrics)     │
#    │ 4. Deploy tuned model ke endpoint                  │
#    └─────────────────────────────────────────────────┘
#
# 2. TRAINING — Infrastructure untuk model training
#    ┌─────────────────────────────────────────────────┐
#    │ VERTEX AI TRAINING:                               │
#    │ - CustomJob: run any training code on GPUs         │
#    │ - HyperparameterTuningJob: auto-tune hyperparams  │
#    │ - Pipeline: orchestrate multi-step training        │
#    │ - Hardware: A100, H100, TPU v5e/v5p               │
#    │ - Distributed: multi-GPU, multi-node              │
#    └─────────────────────────────────────────────────┘
#
# 3. EXPERIMENTS — Track dan compare training runs
#    ┌─────────────────────────────────────────────────┐
#    │ VERTEX AI EXPERIMENTS (MLflow-compatible):         │
#    │ - Experiment: container for multiple runs          │
#    │ - Run: satu training execution                    │
#    │ - Metrics: loss, accuracy, BLEU, etc.             │
#    │ - Parameters: lr, epochs, batch_size              │
#    │ - Artifacts: model weights, plots, logs           │
#    │ - Compare: side-by-side runs comparison           │
#    └─────────────────────────────────────────────────┘
#
# 4. DATASETS — Manage training dan eval datasets
#    ┌─────────────────────────────────────────────────┐
#    │ VERTEX AI DATASETS:                               │
#    │ - Managed datasets (tabular, text, image, video)  │
#    │ - Auto-split: train/validation/test               │
#    │ - Versioning: track dataset changes                │
#    │ - Annotation: label data via UI                   │
#    │ - Import from: GCS, BigQuery, local              │
#    │                                                   │
#    │ FORMAT FINE-TUNING:                                │
#    │ JSONL: {"input": "...", "output": "..."}          │
#    │ Chat: {"messages": [{"role": ..., "content": ...}]}│
#    └─────────────────────────────────────────────────┘

class FineTuneMethod(Enum):
    SFT = "supervised_fine_tuning"
    RLHF = "rlhf"
    LORA = "lora"
    QLORA = "qlora"

class TrainingStatus(Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class DatasetFormat(Enum):
    JSONL = "jsonl"
    CHAT = "chat_messages"
    CSV = "csv"
    PARQUET = "parquet"


# ─────────────────────────────────────────────────
# KOMPONEN 1: Dataset Manager
# ─────────────────────────────────────────────────
class DatasetManager:
    """
    PELAJARAN: Dataset = fondasi fine-tuning.
    Tanpa data berkualitas → model buruk ("garbage in, garbage out").
    """
    def __init__(self):
        self.datasets = {}

    def create_dataset(self, name, records, format_type=DatasetFormat.JSONL,
                       split_ratio=(0.8, 0.1, 0.1)):
        """Create managed dataset with auto-split."""
        dataset_id = str(uuid.uuid4())[:8]
        random.shuffle(records)

        n = len(records)
        train_end = int(n * split_ratio[0])
        val_end = train_end + int(n * split_ratio[1])

        dataset = {
            "id": dataset_id,
            "name": name,
            "format": format_type.value,
            "total_records": n,
            "splits": {
                "train": records[:train_end],
                "validation": records[train_end:val_end],
                "test": records[val_end:],
            },
            "split_sizes": {
                "train": train_end,
                "validation": val_end - train_end,
                "test": n - val_end,
            },
            "version": 1,
            "created_at": time.time(),
        }
        self.datasets[name] = dataset
        print(f"      📊 Dataset '{name}' created: {n} records")
        print(f"         Split: train={dataset['split_sizes']['train']}, "
              f"val={dataset['split_sizes']['validation']}, test={dataset['split_sizes']['test']}")
        return dataset

    def get_split(self, name, split="train"):
        return self.datasets[name]["splits"].get(split, [])

    def add_version(self, name, new_records):
        """Versioned dataset updates."""
        ds = self.datasets[name]
        ds["version"] += 1
        ds["total_records"] += len(new_records)
        ds["splits"]["train"].extend(new_records)
        print(f"      📊 Dataset '{name}' → v{ds['version']} (+{len(new_records)} records)")


# ─────────────────────────────────────────────────
# KOMPONEN 2: Fine Tuning Engine
# ─────────────────────────────────────────────────
class FineTuneJob:
    """
    PELAJARAN: Fine-tune job = satu training run.
    Vertex AI creates a COPY of base model + adapter weights.
    """
    def __init__(self, base_model, dataset_name, method=FineTuneMethod.SFT,
                 hyperparams=None):
        self.job_id = str(uuid.uuid4())[:8]
        self.base_model = base_model
        self.dataset_name = dataset_name
        self.method = method
        self.hyperparams = hyperparams or {
            "epochs": 3,
            "learning_rate": 2e-5,
            "batch_size": 8,
            "warmup_steps": 100,
            "weight_decay": 0.01,
        }
        self.status = TrainingStatus.PENDING
        self.metrics_history = []
        self.best_metric = None
        self.output_model = None
        self.start_time = None
        self.end_time = None

    def simulate_training(self, dataset_size):
        """Simulate training with realistic loss curves."""
        self.status = TrainingStatus.RUNNING
        self.start_time = time.time()
        epochs = self.hyperparams["epochs"]
        lr = self.hyperparams["learning_rate"]

        print(f"      🏋️ Training [{self.method.value}] on {self.base_model}")
        print(f"         Hyperparams: {json.dumps(self.hyperparams)}")

        initial_loss = 2.5 + random.uniform(0, 0.5)
        best_val_loss = float('inf')

        for epoch in range(1, epochs + 1):
            # Simulate loss decay (exponential with noise)
            progress = epoch / epochs
            train_loss = initial_loss * math.exp(-2.0 * progress) + random.uniform(0, 0.1)
            val_loss = train_loss + random.uniform(0.05, 0.2)

            # LoRA: faster convergence
            if self.method in (FineTuneMethod.LORA, FineTuneMethod.QLORA):
                train_loss *= 0.85
                val_loss *= 0.9

            metrics = {
                "epoch": epoch,
                "train_loss": round(train_loss, 4),
                "val_loss": round(val_loss, 4),
                "learning_rate": lr * (1 - 0.5 * progress),  # LR schedule
                "gpu_memory_gb": 24.5 if self.method != FineTuneMethod.QLORA else 8.2,
            }
            self.metrics_history.append(metrics)

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self.best_metric = metrics
                checkpoint = f"checkpoint-epoch{epoch}"

            print(f"         Epoch {epoch}/{epochs}: "
                  f"train_loss={metrics['train_loss']:.4f}, "
                  f"val_loss={metrics['val_loss']:.4f}, "
                  f"lr={metrics['learning_rate']:.6f}, "
                  f"gpu={metrics['gpu_memory_gb']}GB")

        self.status = TrainingStatus.SUCCEEDED
        self.end_time = time.time()
        self.output_model = f"ft-{self.base_model}-{self.job_id}"
        print(f"         ✅ Training complete: {self.output_model}")
        print(f"         Best val_loss: {best_val_loss:.4f} at epoch {self.best_metric['epoch']}")
        return self.output_model


# ─────────────────────────────────────────────────
# KOMPONEN 3: LoRA Adapter
# ─────────────────────────────────────────────────
class LoRAConfig:
    """
    PELAJARAN KUNCI — LoRA (Low-Rank Adaptation):

    Normal fine-tuning: update W (d × d matrix, milyaran params)
    LoRA: W' = W + Δ W, dimana Δ W = A × B
    A: (d × r) matrix | B: (r × d) matrix | r << d

    Contoh: d=4096, r=16
    Full: 4096 × 4096 = 16.7 juta params per layer
    LoRA: (4096 × 16) + (16 × 4096) = 131,072 params per layer
    → 99.2% reduction!

    QLoRA: Base model di-quantize ke 4-bit + LoRA adapters float16
    → GPU 24GB bisa fine-tune model 70B!
    """
    def __init__(self, rank=16, alpha=32, dropout=0.05, target_modules=None):
        self.rank = rank
        self.alpha = alpha
        self.dropout = dropout
        self.target_modules = target_modules or ["q_proj", "v_proj", "k_proj", "o_proj"]
        self.scaling = alpha / rank

    def estimate_params(self, model_dim=4096, num_layers=32):
        """Estimate trainable parameters."""
        params_per_module = 2 * model_dim * self.rank  # A + B matrices
        total_modules = len(self.target_modules) * num_layers
        total_trainable = params_per_module * total_modules
        full_params = model_dim * model_dim * len(self.target_modules) * num_layers
        reduction = (1 - total_trainable / full_params) * 100

        return {
            "trainable_params": total_trainable,
            "full_params": full_params,
            "reduction_pct": round(reduction, 2),
            "rank": self.rank,
            "modules": self.target_modules,
        }


# ─────────────────────────────────────────────────
# KOMPONEN 4: Experiment Tracker
# ─────────────────────────────────────────────────
class ExperimentTracker:
    """
    PELAJARAN: Experiment tracking = MLflow-style lifecycle.
    Tanpa tracking → tidak tahu mana model terbaik!
    """
    def __init__(self, experiment_name):
        self.name = experiment_name
        self.runs = {}

    def start_run(self, run_name, params=None):
        run_id = str(uuid.uuid4())[:8]
        run = {
            "id": run_id,
            "name": run_name,
            "params": params or {},
            "metrics": {},
            "artifacts": [],
            "status": "RUNNING",
            "start_time": time.time(),
            "end_time": None,
        }
        self.runs[run_id] = run
        print(f"      📝 Run '{run_name}' started (id={run_id})")
        return run_id

    def log_metric(self, run_id, key, value, step=None):
        run = self.runs[run_id]
        if key not in run["metrics"]:
            run["metrics"][key] = []
        run["metrics"][key].append({"value": value, "step": step})

    def log_params(self, run_id, params):
        self.runs[run_id]["params"].update(params)

    def log_artifact(self, run_id, artifact_path):
        self.runs[run_id]["artifacts"].append(artifact_path)

    def end_run(self, run_id, status="SUCCEEDED"):
        self.runs[run_id]["status"] = status
        self.runs[run_id]["end_time"] = time.time()

    def compare_runs(self, metric_key="val_loss"):
        """Compare all runs by a metric."""
        comparison = []
        for run_id, run in self.runs.items():
            values = run["metrics"].get(metric_key, [])
            best = min((v["value"] for v in values), default=float('inf'))
            comparison.append({
                "run": run["name"],
                "best_" + metric_key: round(best, 4),
                "params": run["params"],
                "status": run["status"],
            })
        comparison.sort(key=lambda x: x[f"best_{metric_key}"])
        return comparison


# ─────────────────────────────────────────────────
# KOMPONEN 5: Hyperparameter Tuning
# ─────────────────────────────────────────────────
class HyperparameterTuner:
    """
    PELAJARAN: Bayesian hyperparameter optimization.
    Vertex AI: define search space → auto-try combinations.
    """
    def __init__(self, search_space):
        self.search_space = search_space
        self.trials = []

    def sample(self):
        """Random sample from search space."""
        config = {}
        for param, space in self.search_space.items():
            if space["type"] == "float":
                config[param] = random.uniform(space["min"], space["max"])
            elif space["type"] == "int":
                config[param] = random.randint(space["min"], space["max"])
            elif space["type"] == "choice":
                config[param] = random.choice(space["values"])
        return config

    def run_trials(self, n_trials, train_fn):
        """Run n_trials with different hyperparams."""
        print(f"      🔬 Hyperparameter search: {n_trials} trials")
        for i in range(n_trials):
            config = self.sample()
            score = train_fn(config)
            self.trials.append({"trial": i + 1, "config": config, "score": score})
            print(f"         Trial {i+1}: score={score:.4f} | {json.dumps({k: round(v, 6) if isinstance(v, float) else v for k, v in config.items()})}")

        best = min(self.trials, key=lambda t: t["score"])
        print(f"      🏆 Best trial: #{best['trial']} (score={best['score']:.4f})")
        return best


# ==========================================
# 🧪 TEST
# ==========================================
if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')

    print("=" * 70)
    print("🎓 AGENT MOTHER: Fine Tuning + Training + Experiments + Datasets")
    print("=" * 70)
    print()
    print("📖 PROSES PEMBELAJARAN:")
    print("   Fine Tuning: SFT, RLHF, LoRA, QLoRA (4 metode)")
    print("   Training: CustomJob, Hyperparameter tuning, GPUs")
    print("   Experiments: MLflow-style tracking (runs, metrics, compare)")
    print("   Datasets: managed, versioned, auto-split")

    # ── PART 1: Datasets ──
    print(f"\n{'─'*60}")
    print("📋 PART 1: Dataset Management")
    dm = DatasetManager()

    # Create SFT dataset
    sft_records = [
        {"input": f"Apa itu {t}?", "output": f"{t} adalah konsep penting dalam AI."}
        for t in ["RAG", "fine-tuning", "LoRA", "embedding", "tokenizer",
                  "attention", "transformer", "RLHF", "quantization", "KV cache"]
    ]
    dataset = dm.create_dataset("agent_sft_v1", sft_records, DatasetFormat.JSONL)

    # Version update
    new_records = [{"input": "Apa itu agent?", "output": "Agent adalah AI yang bisa bertindak otonom."}]
    dm.add_version("agent_sft_v1", new_records)

    # ── PART 2: LoRA Config ──
    print(f"\n{'─'*60}")
    print("📋 PART 2: LoRA Configuration")
    lora = LoRAConfig(rank=16, alpha=32, dropout=0.05)
    estimates = lora.estimate_params(model_dim=4096, num_layers=32)
    print(f"   LoRA r={lora.rank}, alpha={lora.alpha}, scaling={lora.scaling}")
    print(f"   Trainable params: {estimates['trainable_params']:,}")
    print(f"   Full params:      {estimates['full_params']:,}")
    print(f"   Reduction:        {estimates['reduction_pct']}%")
    print(f"   Target modules:   {estimates['modules']}")

    # ── PART 3: Fine Tuning ──
    print(f"\n{'─'*60}")
    print("📋 PART 3: Fine Tuning (3 methods)")

    # SFT
    print("\n   [Method 1: Supervised Fine-Tuning]")
    sft_job = FineTuneJob("gemini-2.0-flash", "agent_sft_v1",
                          method=FineTuneMethod.SFT,
                          hyperparams={"epochs": 3, "learning_rate": 2e-5, "batch_size": 8,
                                       "warmup_steps": 100, "weight_decay": 0.01})
    sft_model = sft_job.simulate_training(len(sft_records))

    # LoRA
    print("\n   [Method 2: LoRA]")
    lora_job = FineTuneJob("llama-3.2-8b", "agent_sft_v1",
                           method=FineTuneMethod.LORA,
                           hyperparams={"epochs": 3, "learning_rate": 1e-4, "batch_size": 4,
                                        "warmup_steps": 50, "weight_decay": 0.0})
    lora_model = lora_job.simulate_training(len(sft_records))

    # QLoRA
    print("\n   [Method 3: QLoRA (4-bit quantized)]")
    qlora_job = FineTuneJob("llama-3.2-70b", "agent_sft_v1",
                            method=FineTuneMethod.QLORA,
                            hyperparams={"epochs": 3, "learning_rate": 5e-5, "batch_size": 2,
                                         "warmup_steps": 50, "weight_decay": 0.0})
    qlora_model = qlora_job.simulate_training(len(sft_records))

    # ── PART 4: Experiment Tracking ──
    print(f"\n{'─'*60}")
    print("📋 PART 4: Experiment Tracking")
    tracker = ExperimentTracker("agent_fine_tuning")

    for job, name in [(sft_job, "sft_run"), (lora_job, "lora_run"), (qlora_job, "qlora_run")]:
        rid = tracker.start_run(name, job.hyperparams)
        for m in job.metrics_history:
            tracker.log_metric(rid, "val_loss", m["val_loss"], step=m["epoch"])
        tracker.end_run(rid)

    print("\n   📊 Comparing runs:")
    comparison = tracker.compare_runs("val_loss")
    for c in comparison:
        print(f"      {c['run']}: best_val_loss={c['best_val_loss']:.4f} ({c['status']})")

    # ── PART 5: Hyperparameter Tuning ──
    print(f"\n{'─'*60}")
    print("📋 PART 5: Hyperparameter Tuning")
    tuner = HyperparameterTuner({
        "learning_rate": {"type": "float", "min": 1e-6, "max": 1e-3},
        "batch_size": {"type": "choice", "values": [2, 4, 8, 16]},
        "epochs": {"type": "int", "min": 1, "max": 5},
    })

    def mock_train(config):
        return 2.0 * math.exp(-config["learning_rate"] * 1000) + random.uniform(0, 0.3)

    best = tuner.run_trials(5, mock_train)

    print(f"\n{'='*70}")
    print("✅ Fine Tuning + Training + Experiments + Datasets: DIPELAJARI.")
    print("   Fine Tuning: SFT, RLHF, LoRA (99.2% param reduction), QLoRA ✓")
    print("   LoRA: rank=16, d=4096 → trainable 131K vs full 2.1B params ✓")
    print("   Datasets: JSONL/Chat format, versioned, auto-split ✓")
    print("   Experiments: MLflow-style tracking + compare runs ✓")
    print("   Hyperparameter tuning: random search + best selection ✓")
    print(f"{'='*70}")
