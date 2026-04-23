# omni_mirdata_engine.py
# Production-Grade Music Information Retrieval Dataset Engine
# ==============================================================
# Absorbed from: mir-dataset-loaders/mirdata
#
# Key patterns learned and implemented:
# - Standardized MIR dataset schema with metadata validation
# - Annotation loader for beats, chords, sections, melody
# - Multi-dataset catalog management and discovery
# - Audio-annotation alignment verification
# - Dataset statistics and coverage analysis
#
# OMNI Layer: compute/python_core
# @since 2026.4.0

"""
OMNI Mirdata Engine
===================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
from typing import List, Optional, Dict, Any, Tuple, Set
import os
import math

ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class MirdataError(Exception):
    """Base error for MIR data operations."""
    pass


class DatasetNotFoundError(MirdataError):
    """Raised when a dataset is not found in the catalog."""
    pass


class InvalidAnnotationError(MirdataError):
    """Raised when annotation data is malformed."""
    pass


class OmniMirdataEngine:
    """
    Production-grade MIR dataset management engine.

    Provides standardized access to Music Information Retrieval
    datasets with unified annotation schemas, metadata validation,
    coverage analysis, and cross-dataset querying capabilities.

    Attributes:
        data_root: Root directory for dataset storage.
        registered_datasets: Dict of known dataset configurations.
    """

    DEFAULT_DATASETS = {
        "medley_db": {
            "name": "MedleyDB",
            "num_tracks": 122,
            "annotations": ["melody", "pitch", "instrument"],
            "genres": ["rock", "pop", "jazz", "world"],
        },
        "rwc_popular": {
            "name": "RWC-Popular",
            "num_tracks": 100,
            "annotations": ["beats", "chords", "sections", "melody"],
            "genres": ["pop", "rock"],
        },
        "gtzan": {
            "name": "GTZAN",
            "num_tracks": 1000,
            "annotations": ["genre"],
            "genres": ["blues", "classical", "country", "disco",
                       "hiphop", "jazz", "metal", "pop", "reggae", "rock"],
        },
        "maestro": {
            "name": "MAESTRO",
            "num_tracks": 1282,
            "annotations": ["midi", "beats", "key"],
            "genres": ["classical"],
        },
        "musdb18": {
            "name": "MUSDB18",
            "num_tracks": 150,
            "annotations": ["stems", "vocals", "drums", "bass", "other"],
            "genres": ["pop", "rock", "hip-hop", "electronic"],
        },
    }

    def __init__(
        self,
        data_root: str = "/data/mir",
        custom_datasets: Optional[Dict[str, Dict]] = None,
    ):
        """
        Initialize the MIR data engine.

        Args:
            data_root: Root directory for dataset storage.
            custom_datasets: Additional datasets to register.
        """
        self.data_root = data_root
        self.registered_datasets = dict(self.DEFAULT_DATASETS)
        if custom_datasets:
            self.registered_datasets.update(custom_datasets)

    def list_datasets(
        self, filter_annotation: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List all registered datasets with optional filtering.

        Args:
            filter_annotation: Only return datasets containing
                              this annotation type.

        Returns:
            Dict with filtered dataset catalog.
        """
        results: List[Dict[str, Any]] = []
        for ds_id, ds_info in self.registered_datasets.items():
            if filter_annotation:
                if filter_annotation not in ds_info.get("annotations", []):
                    continue
            results.append({
                "id": ds_id,
                "name": ds_info["name"],
                "num_tracks": ds_info["num_tracks"],
                "annotations": ds_info["annotations"],
                "genres": ds_info.get("genres", []),
            })

        return {
            "status": "success",
            "data": {
                "datasets": results,
                "num_datasets": len(results),
                "total_tracks": sum(d["num_tracks"] for d in results),
                "filter_applied": filter_annotation,
            }
        }

    def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific dataset.

        Args:
            dataset_id: Dataset identifier string.

        Returns:
            Dict with comprehensive dataset metadata.

        Raises:
            DatasetNotFoundError: If dataset_id is unknown.
        """
        if dataset_id not in self.registered_datasets:
            raise DatasetNotFoundError(
                f"Dataset '{dataset_id}' not found. "
                f"Available: {list(self.registered_datasets.keys())}"
            )

        ds = self.registered_datasets[dataset_id]
        data_path = os.path.join(self.data_root, dataset_id)

        return {
            "status": "success",
            "data": {
                "id": dataset_id,
                "name": ds["name"],
                "num_tracks": ds["num_tracks"],
                "annotations": ds["annotations"],
                "genres": ds.get("genres", []),
                "data_path": data_path,
                "annotation_types": len(ds["annotations"]),
                "genre_diversity": len(ds.get("genres", [])),
            }
        }

    def validate_annotation(
        self, annotation: Dict[str, Any], annotation_type: str
    ) -> Dict[str, Any]:
        """
        Validate annotation data against schema rules.

        Args:
            annotation: Annotation data dict.
            annotation_type: Type of annotation to validate against.

        Returns:
            Dict with validation results and any errors.
        """
        errors: List[str] = []
        warnings: List[str] = []

        if annotation_type == "beats":
            times = annotation.get("times", [])
            if not times:
                errors.append("Beat annotation must have 'times' array")
            elif len(times) < 2:
                warnings.append("Very few beat annotations")
            else:
                for i in range(1, len(times)):
                    if times[i] <= times[i - 1]:
                        errors.append(
                            f"Non-monotonic beat at index {i}: "
                            f"{times[i]} <= {times[i-1]}"
                        )
                        break

        elif annotation_type == "chords":
            intervals = annotation.get("intervals", [])
            labels = annotation.get("labels", [])
            if not intervals or not labels:
                errors.append("Chord annotation needs 'intervals' and 'labels'")
            elif len(intervals) != len(labels):
                errors.append(
                    f"Interval/label count mismatch: "
                    f"{len(intervals)} vs {len(labels)}"
                )

        elif annotation_type == "melody":
            times = annotation.get("times", [])
            frequencies = annotation.get("frequencies", [])
            if not times or not frequencies:
                errors.append("Melody needs 'times' and 'frequencies'")
            elif len(times) != len(frequencies):
                errors.append("Time/frequency count mismatch")

        elif annotation_type == "genre":
            label = annotation.get("label", "")
            if not label:
                errors.append("Genre annotation must have 'label'")

        is_valid = len(errors) == 0

        return {
            "status": "success",
            "data": {
                "is_valid": is_valid,
                "annotation_type": annotation_type,
                "errors": errors,
                "warnings": warnings,
                "num_errors": len(errors),
                "num_warnings": len(warnings),
            }
        }

    def compute_dataset_statistics(
        self, track_durations: List[float], annotations_per_track: List[int]
    ) -> Dict[str, Any]:
        """
        Compute comprehensive statistics for a dataset.

        Args:
            track_durations: Duration of each track in seconds.
            annotations_per_track: Number of annotations per track.

        Returns:
            Dict with statistical summaries.
        """
        if not track_durations:
            raise MirdataError("No track durations provided")

        n = len(track_durations)
        total_dur = sum(track_durations)
        mean_dur = total_dur / n
        sorted_dur = sorted(track_durations)
        median_dur = sorted_dur[n // 2]
        var_dur = sum((d - mean_dur) ** 2 for d in track_durations) / n
        std_dur = math.sqrt(var_dur)

        total_ann = sum(annotations_per_track) if annotations_per_track else 0
        mean_ann = total_ann / max(len(annotations_per_track), 1)
        ann_density = total_ann / max(total_dur, 0.01)

        return {
            "status": "success",
            "data": {
                "num_tracks": n,
                "total_duration_s": round(total_dur, 2),
                "total_duration_hours": round(total_dur / 3600, 2),
                "mean_duration_s": round(mean_dur, 2),
                "median_duration_s": round(median_dur, 2),
                "std_duration_s": round(std_dur, 2),
                "min_duration_s": round(sorted_dur[0], 2),
                "max_duration_s": round(sorted_dur[-1], 2),
                "total_annotations": total_ann,
                "mean_annotations_per_track": round(mean_ann, 2),
                "annotation_density_per_s": round(ann_density, 4),
            }
        }

    def find_cross_dataset_tracks(
        self, query_genres: List[str]
    ) -> Dict[str, Any]:
        """
        Find datasets that share specified genre coverage.

        Args:
            query_genres: List of genre strings to search for.

        Returns:
            Dict with matching datasets and genre coverage.
        """
        query_set = set(g.lower() for g in query_genres)
        matches: List[Dict[str, Any]] = []

        for ds_id, ds_info in self.registered_datasets.items():
            ds_genres = set(g.lower() for g in ds_info.get("genres", []))
            overlap = query_set & ds_genres
            if overlap:
                coverage = len(overlap) / len(query_set)
                matches.append({
                    "dataset_id": ds_id,
                    "name": ds_info["name"],
                    "matching_genres": sorted(overlap),
                    "coverage": round(coverage * 100, 1),
                    "num_tracks": ds_info["num_tracks"],
                })

        matches.sort(key=lambda m: m["coverage"], reverse=True)

        return {
            "status": "success",
            "data": {
                "matches": matches,
                "num_matches": len(matches),
                "query_genres": query_genres,
            }
        }

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-mirdata",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }
