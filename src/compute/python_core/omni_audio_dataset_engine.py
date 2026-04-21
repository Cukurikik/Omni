# ===========================================================================
# OMNI AUDIO DATASET ENGINE (SEMESTER 5 — BATCH 4)
# ===========================================================================
# Absorbed From  : DagsHub/audio-datasets
# Logic Inherited: Compute Layer (ML Audio Dataset Management)
# ===========================================================================
"""
OMNI Audio Dataset Engine
=========================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
import logging
from typing import Dict, Any, List, Optional
import os
import json


ENGINE_VERSION = "1.0.0-omni"

logger = logging.getLogger("OmniAudioDatasetEngine")

class OmniAudioDatasetEngine:
    """
    Manages ML Audio Dataset pipelines: cataloging, metadata normalization,
    sample rate validation, and train/test splitting for AI training.
    """

    SUPPORTED_FORMATS = {"wav", "mp3", "flac", "ogg", "m4a"}
    DEFAULT_SAMPLE_RATE = 16000

    def __init__(self, dataset_root: str = ".omni_audio_datasets"):
        """Initialize OmniAudioDatasetEngine."""
        self._dataset_root = dataset_root
        self._catalog: List[Dict[str, Any]] = []
        logger.info(f"[OmniAudioDataset] Engine online. Root: {self._dataset_root}")

    def register_audio_file(self, file_path: str, label: str, duration_seconds: float, sample_rate: int = 16000) -> Dict[str, Any]:
        """Registers a single audio file entry into the dataset catalog."""
        ext = os.path.splitext(file_path)[1].lstrip(".").lower()
        if ext not in self.SUPPORTED_FORMATS:
            return {"status": "error", "error": f"Unsupported format: .{ext}. Allowed: {self.SUPPORTED_FORMATS}"}
        entry = {
            "path": file_path, "label": label,
            "duration_s": duration_seconds, "sample_rate": sample_rate,
            "format": ext, "needs_resample": sample_rate != self.DEFAULT_SAMPLE_RATE
        }
        self._catalog.append(entry)
        return {"status": "success", "data": entry}

    def split_dataset(self, train_ratio: float = 0.8) -> Dict[str, Any]:
        """Splits the catalog into train/test sets for ML pipeline consumption."""
        if not self._catalog:
            return {"status": "error", "error": "Catalog is empty. Register files first."}
        split_idx = int(len(self._catalog) * train_ratio)
        return {
            "status": "success",
            "data": {"train": self._catalog[:split_idx], "test": self._catalog[split_idx:],
                      "train_count": split_idx, "test_count": len(self._catalog) - split_idx}
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Returns summary statistics of the current dataset catalog."""
        if not self._catalog:
            return {"status": "success", "data": {"total": 0}}
        total_duration = sum(e["duration_s"] for e in self._catalog)
        labels = set(e["label"] for e in self._catalog)
        return {"status": "success", "data": {
            "total_files": len(self._catalog), "total_duration_s": round(total_duration, 2),
            "unique_labels": len(labels), "label_list": sorted(labels),
            "needs_resample_count": sum(1 for e in self._catalog if e["needs_resample"])
        }}

    def evaluate_health(self) -> Dict[str, Any]:
        """Performs evaluate health operation for OmniAudioDatasetEngine."""
        return {"engine": "OmniAudioDatasetEngine", "layer": "Compute", "status": "healthy",
                "catalog_size": len(self._catalog), "learned_from": "DagsHub/audio-datasets"}

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-audio-dataset",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
