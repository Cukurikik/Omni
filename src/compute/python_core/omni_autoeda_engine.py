"""
OMNI Autoeda Engine
===================
Production-grade engine for the OMNI Framework.

OMNI Layer: compute (Python)
"""
ENGINE_VERSION = "1.0.0-omni"
"""
OMNI AutoEDA Engine — Automated Exploratory Data Analysis
==========================================================
Production-grade engine for automated data profiling, statistical analysis,
visualization recommendation, and report generation.

Inspired by: github.com/mstaniak/autoEDA-resources
OMNI Layer: Compute (Python)
"""

import os
import json
import math
import hashlib
import logging
import threading
import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger("omni.autoeda")


# ─────────────────────────────────────────────
# Section 1: Core Data Types
# ─────────────────────────────────────────────

class ColumnType(Enum):
    """Type enumeration for ColumnType."""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    TEXT = "text"
    BOOLEAN = "boolean"
    IDENTIFIER = "identifier"
    UNKNOWN = "unknown"


class VisualizationType(Enum):
    """Type enumeration for VisualizationType."""
    HISTOGRAM = "histogram"
    BAR_CHART = "bar_chart"
    BOX_PLOT = "box_plot"
    SCATTER_PLOT = "scatter_plot"
    LINE_CHART = "line_chart"
    HEATMAP = "heatmap"
    VIOLIN_PLOT = "violin_plot"
    PIE_CHART = "pie_chart"
    PAIR_PLOT = "pair_plot"
    CORRELATION_MATRIX = "correlation_matrix"
    TIME_SERIES = "time_series"
    DISTRIBUTION = "distribution"
    COUNT_PLOT = "count_plot"
    MISSING_MAP = "missing_map"
    PARALLEL_COORDINATES = "parallel_coordinates"


class DataQualityLevel(Enum):
    """Production-grade Data Quality Level component."""
    EXCELLENT = "excellent"     # >95% complete, no anomalies
    GOOD = "good"               # >85% complete, minor issues
    MODERATE = "moderate"       # >70% complete, some issues
    POOR = "poor"               # >50% complete, significant issues
    CRITICAL = "critical"       # <50% complete, major issues


@dataclass
class ColumnProfile:
    """Complete statistical profile for a single column."""
    name: str
    dtype: str
    inferred_type: ColumnType
    total_count: int
    missing_count: int
    missing_pct: float
    unique_count: int
    unique_pct: float
    # Numeric stats
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min_val: Optional[float] = None
    max_val: Optional[float] = None
    q1: Optional[float] = None
    q3: Optional[float] = None
    iqr: Optional[float] = None
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    outlier_count: int = 0
    zero_count: int = 0
    negative_count: int = 0
    # Categorical stats
    top_values: Optional[List[Tuple[str, int]]] = None
    entropy: Optional[float] = None
    # Text stats
    avg_length: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    # Recommendations
    recommended_viz: List[VisualizationType] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class CorrelationResult:
    """Correlation between two columns."""
    column_a: str
    column_b: str
    pearson: Optional[float] = None
    spearman: Optional[float] = None
    cramers_v: Optional[float] = None
    strength: str = "none"  # none, weak, moderate, strong


@dataclass
class DatasetProfile:
    """Complete profile for an entire dataset."""
    name: str
    file_path: Optional[str]
    row_count: int
    column_count: int
    memory_bytes: int
    columns: Dict[str, ColumnProfile]
    correlations: List[CorrelationResult]
    data_quality: DataQualityLevel
    quality_score: float
    duplicate_rows: int
    duplicate_pct: float
    insights: List[str]
    recommended_actions: List[str]
    profiled_at: str
    profiling_duration_ms: float
    checksum: str


@dataclass
class EDASession:
    """Active EDA session tracking."""
    session_id: str
    dataset_name: str
    started_at: str
    profiles: List[str] = field(default_factory=list)
    reports_generated: int = 0
    total_rows_processed: int = 0


# ─────────────────────────────────────────────
# Section 2: Statistical Utilities
# ─────────────────────────────────────────────

class StatisticsEngine:
    """Pure-Python statistical computation engine — zero external dependencies."""

    def __init__(self, config=None):
        """Initialize StatisticsEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True

    @staticmethod
    def mean(values: List[float]) -> float:
        """Performs mean operation for StatisticsEngine."""
        if not values:
            return 0.0
        return sum(values) / len(values)

    @staticmethod
    def median(values: List[float]) -> float:
        """Performs median operation for StatisticsEngine."""
        if not values:
            return 0.0
        sorted_v = sorted(values)
        n = len(sorted_v)
        mid = n // 2
        if n % 2 == 0:
            return (sorted_v[mid - 1] + sorted_v[mid]) / 2
        return sorted_v[mid]

    @staticmethod
    def std(values: List[float], ddof: int = 1) -> float:
        """Performs std operation for StatisticsEngine."""
        if len(values) < 2:
            return 0.0
        avg = StatisticsEngine.mean(values)
        variance = sum((x - avg) ** 2 for x in values) / (len(values) - ddof)
        return math.sqrt(variance)

    @staticmethod
    def percentile(values: List[float], pct: float) -> float:
        """Performs percentile operation for StatisticsEngine."""
        if not values:
            return 0.0
        sorted_v = sorted(values)
        k = (len(sorted_v) - 1) * pct / 100.0
        f = math.floor(k)
        c = math.ceil(k)
        if f == c:
            return sorted_v[int(k)]
        return sorted_v[int(f)] * (c - k) + sorted_v[int(c)] * (k - f)

    @staticmethod
    def skewness(values: List[float]) -> float:
        """Performs skewness operation for StatisticsEngine."""
        n = len(values)
        if n < 3:
            return 0.0
        avg = StatisticsEngine.mean(values)
        s = StatisticsEngine.std(values)
        if s == 0:
            return 0.0
        m3 = sum((x - avg) ** 3 for x in values) / n
        return m3 / (s ** 3)

    @staticmethod
    def kurtosis(values: List[float]) -> float:
        """Performs kurtosis operation for StatisticsEngine."""
        n = len(values)
        if n < 4:
            return 0.0
        avg = StatisticsEngine.mean(values)
        s = StatisticsEngine.std(values)
        if s == 0:
            return 0.0
        m4 = sum((x - avg) ** 4 for x in values) / n
        return (m4 / (s ** 4)) - 3.0

    @staticmethod
    def entropy(counts: List[int]) -> float:
        """Performs entropy operation for StatisticsEngine."""
        total = sum(counts)
        if total == 0:
            return 0.0
        ent = 0.0
        for c in counts:
            if c > 0:
                p = c / total
                ent -= p * math.log2(p)
        return ent

    @staticmethod
    def pearson_correlation(x: List[float], y: List[float]) -> Optional[float]:
        """Performs pearson correlation operation for StatisticsEngine."""
        n = len(x)
        if n != len(y) or n < 3:
            return None
        mx = StatisticsEngine.mean(x)
        my = StatisticsEngine.mean(y)
        num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
        dx = math.sqrt(sum((xi - mx) ** 2 for xi in x))
        dy = math.sqrt(sum((yi - my) ** 2 for yi in y))
        if dx == 0 or dy == 0:
            return None
        return num / (dx * dy)

    @staticmethod
    def spearman_correlation(x: List[float], y: List[float]) -> Optional[float]:
        """Performs spearman correlation operation for StatisticsEngine."""
        n = len(x)
        if n != len(y) or n < 3:
            return None

        def rank(vals):
            indexed = sorted(enumerate(vals), key=lambda t: t[1])
            ranks = [0.0] * n
            i = 0
            while i < n:
                j = i
                while j < n - 1 and indexed[j][1] == indexed[j + 1][1]:
                    j += 1
                avg_rank = (i + j) / 2.0 + 1
                for k in range(i, j + 1):
                    ranks[indexed[k][0]] = avg_rank
                i = j + 1
            return ranks

        rx = rank(x)
        ry = rank(y)
        return StatisticsEngine.pearson_correlation(rx, ry)

    @staticmethod
    def detect_outliers_iqr(values: List[float]) -> List[int]:
        """Performs detect outliers iqr operation for StatisticsEngine."""
        q1 = StatisticsEngine.percentile(values, 25)
        q3 = StatisticsEngine.percentile(values, 75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        return [i for i, v in enumerate(values) if v < lower or v > upper]

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-statistics",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }


# ─────────────────────────────────────────────
# Section 3: Data Loader
# ─────────────────────────────────────────────

class DataLoader:
    """Universal data loader supporting CSV, TSV, JSON, and JSONL."""

    SUPPORTED_FORMATS = {".csv", ".tsv", ".json", ".jsonl", ".txt"}

    @staticmethod
    def load(file_path: str) -> Tuple[List[str], List[List[Any]]]:
        """Load data file and return (headers, rows)."""
        ext = Path(file_path).suffix.lower()
        if ext == ".csv":
            return DataLoader._load_csv(file_path, ",")
        elif ext == ".tsv" or ext == ".txt":
            return DataLoader._load_csv(file_path, "\t")
        elif ext == ".json":
            return DataLoader._load_json(file_path)
        elif ext == ".jsonl":
            return DataLoader._load_jsonl(file_path)
        else:
            raise ValueError(f"Unsupported format: {ext}. Supported: {DataLoader.SUPPORTED_FORMATS}")

    @staticmethod
    def _load_csv(path: str, delimiter: str) -> Tuple[List[str], List[List[Any]]]:
        rows = []
        headers = []
        with open(path, "r", encoding="utf-8-sig") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                parts = line.split(delimiter)
                if i == 0:
                    headers = [p.strip().strip('"') for p in parts]
                else:
                    row = [DataLoader._parse_value(p.strip().strip('"')) for p in parts]
                    # Pad or truncate to match header count
                    while len(row) < len(headers):
                        row.append(None)
                    rows.append(row[:len(headers)])
        return headers, rows

    @staticmethod
    def _load_json(path: str) -> Tuple[List[str], List[List[Any]]]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            headers = list(data[0].keys())
            for item in data[1:]:
                for k in item.keys():
                    if k not in headers:
                        headers.append(k)
            rows = [[item.get(h) for h in headers] for item in data]
            return headers, rows
        raise ValueError("JSON must be an array of objects")

    @staticmethod
    def _load_jsonl(path: str) -> Tuple[List[str], List[List[Any]]]:
        headers_set: Dict[str, int] = {}
        records = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    obj = json.loads(line)
                    for k in obj.keys():
                        if k not in headers_set:
                            headers_set[k] = len(headers_set)
                    records.append(obj)
        headers = sorted(headers_set.keys(), key=lambda k: headers_set[k])
        rows = [[rec.get(h) for h in headers] for rec in records]
        return headers, rows

    @staticmethod
    def _parse_value(val: str) -> Any:
        if val == "" or val.lower() in ("null", "none", "na", "n/a", "nan", ""):
            return None
        try:
            if "." in val:
                return float(val)
            return int(val)
        except (ValueError, TypeError):
            return val


# ─────────────────────────────────────────────
# Section 4: Column Type Inference
# ─────────────────────────────────────────────

class TypeInferenceEngine:
    """Automatically infers column semantic types from data samples."""

    def __init__(self, config=None):
        """Initialize TypeInferenceEngine."""
        self.config = config or {}
        self.engine_id = __import__("uuid").uuid4().hex
        self.is_active = True

    DATE_PATTERNS = [
        "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y",
        "%m-%d-%Y", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ",
    ]

    @staticmethod
    def infer(name: str, values: List[Any], total: int) -> ColumnType:
        """Performs infer operation for TypeInferenceEngine."""
        non_null = [v for v in values if v is not None]
        if not non_null:
            return ColumnType.UNKNOWN

        sample = non_null[:min(500, len(non_null))]

        # Check boolean
        bool_vals = {"true", "false", "yes", "no", "0", "1", "t", "f", "y", "n"}
        if all(str(v).lower().strip() in bool_vals for v in sample):
            return ColumnType.BOOLEAN

        # Check numeric
        numeric_count = 0
        for v in sample:
            if isinstance(v, (int, float)):
                numeric_count += 1
            else:
                try:
                    float(str(v))
                    numeric_count += 1
                except (ValueError, TypeError):
                    pass
        if numeric_count / len(sample) > 0.85:
            return ColumnType.NUMERIC

        # Check datetime
        date_count = 0
        for v in sample[:50]:
            s = str(v).strip()
            for fmt in TypeInferenceEngine.DATE_PATTERNS:
                try:
                    datetime.strptime(s, fmt)
                    date_count += 1
                    break
                except (ValueError, TypeError):
                    pass
        if date_count / min(50, len(sample)) > 0.7:
            return ColumnType.DATETIME

        # Check identifier (high cardinality, short values)
        unique_ratio = len(set(str(v) for v in sample)) / len(sample)
        name_lower = name.lower()
        if unique_ratio > 0.95 and any(kw in name_lower for kw in ("id", "uuid", "key", "code", "hash")):
            return ColumnType.IDENTIFIER

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine_id": "omni-type-inference",
            "version": getattr(self, "VERSION", "1.0.0"),
            "status": "operational",
        }

        # Check text (long strings)
        avg_len = sum(len(str(v)) for v in sample) / len(sample)
        if avg_len > 100:
            return ColumnType.TEXT

        # Default to categorical
        return ColumnType.CATEGORICAL


# ─────────────────────────────────────────────
# Section 5: Visualization Recommender
# ─────────────────────────────────────────────

class VizRecommender:
    """Recommends visualization types based on column profiles, following
    principles from VizML and the Rank-by-Feature framework."""

    @staticmethod
    def recommend_univariate(profile: ColumnProfile) -> List[VisualizationType]:
        """Execute recommend univariate operation for VizRecommender."""
        recs = []
        if profile.inferred_type == ColumnType.NUMERIC:
            recs.append(VisualizationType.HISTOGRAM)
            recs.append(VisualizationType.BOX_PLOT)
            if profile.unique_count < 20:
                recs.append(VisualizationType.BAR_CHART)
            if profile.skewness is not None and abs(profile.skewness) > 1.0:
                recs.append(VisualizationType.VIOLIN_PLOT)
        elif profile.inferred_type == ColumnType.CATEGORICAL:
            if profile.unique_count <= 15:
                recs.append(VisualizationType.BAR_CHART)
                recs.append(VisualizationType.PIE_CHART)
            else:
                recs.append(VisualizationType.BAR_CHART)
                recs.append(VisualizationType.COUNT_PLOT)
        elif profile.inferred_type == ColumnType.DATETIME:
            recs.append(VisualizationType.TIME_SERIES)
            recs.append(VisualizationType.LINE_CHART)
        elif profile.inferred_type == ColumnType.BOOLEAN:
            recs.append(VisualizationType.BAR_CHART)
            recs.append(VisualizationType.PIE_CHART)
        elif profile.inferred_type == ColumnType.TEXT:
            recs.append(VisualizationType.DISTRIBUTION)
        return recs

    @staticmethod
    def recommend_bivariate(
        type_a: ColumnType, type_b: ColumnType
    ) -> List[VisualizationType]:
        """Execute recommend bivariate operation for VizRecommender."""
        if type_a == ColumnType.NUMERIC and type_b == ColumnType.NUMERIC:
            return [VisualizationType.SCATTER_PLOT, VisualizationType.HEATMAP]
        elif type_a == ColumnType.NUMERIC and type_b == ColumnType.CATEGORICAL:
            return [VisualizationType.BOX_PLOT, VisualizationType.VIOLIN_PLOT]
        elif type_a == ColumnType.CATEGORICAL and type_b == ColumnType.CATEGORICAL:
            return [VisualizationType.HEATMAP, VisualizationType.COUNT_PLOT]
        elif type_a == ColumnType.DATETIME and type_b == ColumnType.NUMERIC:
            return [VisualizationType.LINE_CHART, VisualizationType.TIME_SERIES]
        return [VisualizationType.BAR_CHART]

    @staticmethod
    def recommend_multivariate(numeric_cols: int) -> List[VisualizationType]:
        """Execute recommend multivariate operation for VizRecommender."""
        recs = []
        if numeric_cols >= 2:
            recs.append(VisualizationType.CORRELATION_MATRIX)
        if numeric_cols >= 3:
            recs.append(VisualizationType.PAIR_PLOT)
        if numeric_cols >= 4:
            recs.append(VisualizationType.PARALLEL_COORDINATES)
        return recs


# ─────────────────────────────────────────────
# Section 6: Insight Generator
# ─────────────────────────────────────────────

class InsightGenerator:
    """Generates actionable insights from statistical analysis."""

    @staticmethod
    def generate(profiles: Dict[str, ColumnProfile], row_count: int) -> Tuple[List[str], List[str]]:
        """Execute generate operation for InsightGenerator."""
        insights = []
        actions = []

        numeric_cols = [p for p in profiles.values() if p.inferred_type == ColumnType.NUMERIC]
        cat_cols = [p for p in profiles.values() if p.inferred_type == ColumnType.CATEGORICAL]

        # Missing data insights
        high_missing = [p for p in profiles.values() if p.missing_pct > 30]
        if high_missing:
            names = ", ".join(p.name for p in high_missing[:5])
            insights.append(f"⚠️ {len(high_missing)} column(s) have >30% missing data: {names}")
            actions.append("Consider imputation strategies or dropping columns with excessive missing values")

        # Zero-variance detection
        constant_cols = [p for p in profiles.values() if p.unique_count <= 1]
        if constant_cols:
            names = ", ".join(p.name for p in constant_cols)
            insights.append(f"📌 Constant column(s) detected (single unique value): {names}")
            actions.append("Remove constant columns as they provide no analytical value")

        # High cardinality categoricals
        high_card = [p for p in cat_cols if p.unique_pct > 90]
        if high_card:
            names = ", ".join(p.name for p in high_card[:5])
            insights.append(f"🔤 High-cardinality categorical column(s): {names}")
            actions.append("Consider re-encoding or treating as identifiers")

        # Skewness
        skewed = [p for p in numeric_cols if p.skewness is not None and abs(p.skewness) > 2.0]
        if skewed:
            names = ", ".join(p.name for p in skewed[:5])
            insights.append(f"📊 Highly skewed numeric column(s): {names}")
            actions.append("Apply log/sqrt transformation to reduce skewness for modeling")

        # Outliers
        outlier_cols = [p for p in numeric_cols if p.outlier_count > 0]
        if outlier_cols:
            total_outliers = sum(p.outlier_count for p in outlier_cols)
            insights.append(f"🎯 {total_outliers} outlier(s) detected across {len(outlier_cols)} column(s)")
            actions.append("Investigate outliers — consider capping, winsorizing, or removing")

        # Negative values
        neg_cols = [p for p in numeric_cols if p.negative_count > 0]
        if neg_cols:
            names = ", ".join(p.name for p in neg_cols[:5])
            insights.append(f"➖ Column(s) with negative values: {names}")

        # Dataset size insights
        if row_count < 100:
            insights.append("📉 Small dataset — statistical inferences may be unreliable")
            actions.append("Collect more data or use bootstrapping for robust estimates")
        elif row_count > 1_000_000:
            insights.append("📈 Large dataset — consider sampling for exploratory analysis")
            actions.append("Use random sampling or stratified sampling for visualization")

        # Imbalanced categoricals
        for p in cat_cols:
            if p.top_values and len(p.top_values) >= 2:
                top_count = p.top_values[0][1]
                total_non_null = p.total_count - p.missing_count
                if total_non_null > 0 and top_count / total_non_null > 0.8:
                    insights.append(f"⚖️ Imbalanced column '{p.name}': '{p.top_values[0][0]}' dominates ({top_count / total_non_null:.0%})")
                    actions.append(f"Consider resampling or using class weights for '{p.name}'")

        return insights, actions


# ─────────────────────────────────────────────
# Section 7: Report Generator
# ─────────────────────────────────────────────

class ReportGenerator:
    """Generates structured EDA reports in multiple formats."""

    @staticmethod
    def to_json(profile: DatasetProfile) -> str:
        """Generate JSON report."""

        def serialize(obj):
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, (list, tuple)):
                return [serialize(i) for i in obj]
            if isinstance(obj, dict):
                return {k: serialize(v) for k, v in obj.items()}
            if hasattr(obj, "__dataclass_fields__"):
                return {k: serialize(v) for k, v in asdict(obj).items()}
            return obj

        return json.dumps(serialize(profile), indent=2, ensure_ascii=False)

    @staticmethod
    def to_markdown(profile: DatasetProfile) -> str:
        """Generate Markdown report."""
        lines = [
            f"# AutoEDA Report: {profile.name}",
            f"*Generated at: {profile.profiled_at}*",
            "",
            "## Dataset Overview",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Rows | {profile.row_count:,} |",
            f"| Columns | {profile.column_count} |",
            f"| Memory | {profile.memory_bytes / 1024:.1f} KB |",
            f"| Data Quality | {profile.data_quality.value} ({profile.quality_score:.1f}/100) |",
            f"| Duplicate Rows | {profile.duplicate_rows:,} ({profile.duplicate_pct:.1f}%) |",
            f"| Checksum | `{profile.checksum[:12]}...` |",
            f"| Profiling Time | {profile.profiling_duration_ms:.0f} ms |",
            "",
        ]

        # Insights
        if profile.insights:
            lines.append("## Key Insights")
            for ins in profile.insights:
                lines.append(f"- {ins}")
            lines.append("")

        # Actions
        if profile.recommended_actions:
            lines.append("## Recommended Actions")
            for act in profile.recommended_actions:
                lines.append(f"- {act}")
            lines.append("")

        # Column Profiles
        lines.append("## Column Profiles")
        lines.append("| Column | Type | Missing% | Unique | Mean | Std | Viz |")
        lines.append("|--------|------|----------|--------|------|-----|-----|")
        for cp in profile.columns.values():
            mean_s = f"{cp.mean:.2f}" if cp.mean is not None else "—"
            std_s = f"{cp.std:.2f}" if cp.std is not None else "—"
            viz_s = ", ".join(v.value for v in cp.recommended_viz[:2]) if cp.recommended_viz else "—"
            lines.append(
                f"| {cp.name} | {cp.inferred_type.value} | {cp.missing_pct:.1f}% | "
                f"{cp.unique_count} | {mean_s} | {std_s} | {viz_s} |"
            )
        lines.append("")

        # Correlations
        if profile.correlations:
            lines.append("## Top Correlations")
            lines.append("| Column A | Column B | Pearson | Strength |")
            lines.append("|----------|----------|---------|----------|")
            sorted_corr = sorted(
                profile.correlations,
                key=lambda c: abs(c.pearson or 0),
                reverse=True
            )
            for c in sorted_corr[:15]:
                p_s = f"{c.pearson:.3f}" if c.pearson is not None else "—"
                lines.append(f"| {c.column_a} | {c.column_b} | {p_s} | {c.strength} |")
            lines.append("")

        # Warnings
        all_warnings = []
        for cp in profile.columns.values():
            for w in cp.warnings:
                all_warnings.append(f"**{cp.name}**: {w}")
        if all_warnings:
            lines.append("## Warnings")
            for w in all_warnings:
                lines.append(f"- {w}")

        return "\n".join(lines)

    @staticmethod
    def save(profile: DatasetProfile, output_dir: str, fmt: str = "both") -> List[str]:
        """Save report to disk. Returns list of saved file paths."""
        os.makedirs(output_dir, exist_ok=True)
        saved = []
        base = profile.name.replace(" ", "_").lower()

        if fmt in ("json", "both"):
            json_path = os.path.join(output_dir, f"{base}_eda_report.json")
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(ReportGenerator.to_json(profile))
            saved.append(json_path)

        if fmt in ("markdown", "both"):
            md_path = os.path.join(output_dir, f"{base}_eda_report.md")
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(ReportGenerator.to_markdown(profile))
            saved.append(md_path)

        return saved


# ─────────────────────────────────────────────
# Section 8: Main Engine
# ─────────────────────────────────────────────

class OmniAutoEDAEngine:
    """
    OMNI AutoEDA Engine — Production-grade automated EDA.

    Capabilities:
     - Multi-format data loading (CSV, TSV, JSON, JSONL)
     - Automatic column type inference
     - Comprehensive statistical profiling (mean, median, std, skew, kurtosis, outliers)
     - Correlation analysis (Pearson, Spearman)
     - Visualization recommendation (VizML-inspired)
     - Actionable insight generation
     - Report generation (JSON, Markdown)
     - Session management and diagnostics
    """

    def __init__(self, output_dir: Optional[str] = None):
        """Initialize OmniAutoEDAEngine."""
        self._lock = threading.Lock()
        self._started_at = datetime.now(timezone.utc).isoformat()
        self._output_dir = output_dir or os.path.join(os.path.expanduser("~"), ".omni", "autoeda_reports")
        self._stats = StatisticsEngine()
        self._sessions: Dict[str, EDASession] = {}
        self._profiles: Dict[str, DatasetProfile] = {}

        # Counters
        self._total_datasets_profiled = 0
        self._total_rows_processed = 0
        self._total_columns_processed = 0
        self._total_reports_generated = 0
        self._errors: List[str] = []

        logger.info("OmniAutoEDAEngine initialized — output: %s", self._output_dir)

    # ── Public API ──

    def profile_file(self, file_path: str, name: Optional[str] = None) -> DatasetProfile:
        """Profile a data file end-to-end."""
        start = time.monotonic()
        abs_path = os.path.abspath(file_path)

        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Data file not found: {abs_path}")

        dataset_name = name or Path(abs_path).stem
        logger.info("Profiling dataset: %s (%s)", dataset_name, abs_path)

        headers, rows = DataLoader.load(abs_path)
        profile = self.profile_data(headers, rows, dataset_name, abs_path)

        elapsed = (time.monotonic() - start) * 1000
        profile.profiling_duration_ms = elapsed
        logger.info("Profiling complete: %s — %.0fms", dataset_name, elapsed)
        return profile

    def profile_data(
        self,
        headers: List[str],
        rows: List[List[Any]],
        name: str = "untitled",
        file_path: Optional[str] = None,
    ) -> DatasetProfile:
        """Profile raw tabular data (headers + rows)."""
        start = time.monotonic()
        row_count = len(rows)
        col_count = len(headers)

        # Build column values
        col_values: Dict[str, List[Any]] = {h: [] for h in headers}
        for row in rows:
            for i, h in enumerate(headers):
                val = row[i] if i < len(row) else None
                col_values[h].append(val)

        # Checksum
        raw = json.dumps({"headers": headers, "rows_count": row_count}, sort_keys=True)
        checksum = hashlib.sha256(raw.encode()).hexdigest()

        # Profile each column
        col_profiles: Dict[str, ColumnProfile] = {}
        for h in headers:
            col_profiles[h] = self._profile_column(h, col_values[h], row_count)

        # Duplicate detection
        row_hashes = set()
        dup_count = 0
        for row in rows:
            rh = hashlib.md5(str(row).encode()).hexdigest()
            if rh in row_hashes:
                dup_count += 1
            row_hashes.add(rh)

        # Correlations
        numeric_profiles = {n: p for n, p in col_profiles.items() if p.inferred_type == ColumnType.NUMERIC}
        correlations = self._compute_correlations(numeric_profiles, col_values)

        # Insights
        insights, actions = InsightGenerator.generate(col_profiles, row_count)

        # Multivariate viz recommendations
        mv_recs = VizRecommender.recommend_multivariate(len(numeric_profiles))
        if mv_recs:
            insights.append(f"📊 Recommended multivariate viz: {', '.join(v.value for v in mv_recs)}")

        # Missing data map recommendation
        missing_cols = sum(1 for p in col_profiles.values() if p.missing_count > 0)
        if missing_cols >= 2:
            insights.append("🗺️ Multiple columns with missing data — a missing data heatmap is recommended")

        # Data quality score
        quality_score = self._compute_quality_score(col_profiles, dup_count, row_count)
        quality_level = self._score_to_level(quality_score)

        # Memory estimate
        memory_bytes = row_count * col_count * 64  # rough estimate

        elapsed = (time.monotonic() - start) * 1000

        profile = DatasetProfile(
            name=name,
            file_path=file_path,
            row_count=row_count,
            column_count=col_count,
            memory_bytes=memory_bytes,
            columns=col_profiles,
            correlations=correlations,
            data_quality=quality_level,
            quality_score=quality_score,
            duplicate_rows=dup_count,
            duplicate_pct=(dup_count / row_count * 100) if row_count > 0 else 0.0,
            insights=insights,
            recommended_actions=actions,
            profiled_at=datetime.now(timezone.utc).isoformat(),
            profiling_duration_ms=elapsed,
            checksum=checksum,
        )

        with self._lock:
            self._profiles[name] = profile
            self._total_datasets_profiled += 1
            self._total_rows_processed += row_count
            self._total_columns_processed += col_count

        return profile

    def generate_report(
        self, profile: DatasetProfile, fmt: str = "both"
    ) -> List[str]:
        """Generate and save EDA report."""
        saved = ReportGenerator.save(profile, self._output_dir, fmt)
        with self._lock:
            self._total_reports_generated += len(saved)
        logger.info("Report(s) saved: %s", saved)
        return saved

    def quick_profile(self, file_path: str) -> str:
        """One-shot: profile + generate markdown report, return markdown."""
        profile = self.profile_file(file_path)
        return ReportGenerator.to_markdown(profile)

    def compare_datasets(
        self, profile_a: DatasetProfile, profile_b: DatasetProfile
    ) -> Dict[str, Any]:
        """Compare two dataset profiles for schema/quality drift."""
        comparison = {
            "dataset_a": profile_a.name,
            "dataset_b": profile_b.name,
            "row_diff": profile_b.row_count - profile_a.row_count,
            "col_diff": profile_b.column_count - profile_a.column_count,
            "quality_diff": profile_b.quality_score - profile_a.quality_score,
            "new_columns": [],
            "removed_columns": [],
            "type_changes": [],
            "distribution_shifts": [],
        }

        cols_a = set(profile_a.columns.keys())
        cols_b = set(profile_b.columns.keys())
        comparison["new_columns"] = list(cols_b - cols_a)
        comparison["removed_columns"] = list(cols_a - cols_b)

        for col in cols_a & cols_b:
            pa = profile_a.columns[col]
            pb = profile_b.columns[col]
            if pa.inferred_type != pb.inferred_type:
                comparison["type_changes"].append({
                    "column": col,
                    "from": pa.inferred_type.value,
                    "to": pb.inferred_type.value,
                })
            if pa.mean is not None and pb.mean is not None:
                if pa.std and pa.std > 0:
                    shift = abs(pb.mean - pa.mean) / pa.std
                    if shift > 2.0:
                        comparison["distribution_shifts"].append({
                            "column": col,
                            "mean_a": pa.mean,
                            "mean_b": pb.mean,
                            "shift_sigmas": round(shift, 2),
                        })

        return comparison

    def create_session(self, dataset_name: str) -> str:
        """Create a new EDA session for iterative analysis."""
        sid = hashlib.md5(f"{dataset_name}-{time.time()}".encode()).hexdigest()[:12]
        session = EDASession(
            session_id=sid,
            dataset_name=dataset_name,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        with self._lock:
            self._sessions[sid] = session
        return sid

    def get_profile(self, name: str) -> Optional[DatasetProfile]:
        """Retrieve a cached dataset profile by name."""
        return self._profiles.get(name)

    def list_profiles(self) -> List[str]:
        """List all cached dataset profile names."""
        return list(self._profiles.keys())

    # ── OMNI Diagnostics ──

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI-standard diagnostics endpoint."""
        with self._lock:
            return {
                "engine": "OmniAutoEDAEngine",
                "version": "1.0.0",
                "status": "operational",
                "started_at": self._started_at,
                "output_dir": self._output_dir,
                "stats": {
                    "total_datasets_profiled": self._total_datasets_profiled,
                    "total_rows_processed": self._total_rows_processed,
                    "total_columns_processed": self._total_columns_processed,
                    "total_reports_generated": self._total_reports_generated,
                    "active_sessions": len(self._sessions),
                    "cached_profiles": len(self._profiles),
                    "errors": len(self._errors),
                },
                "capabilities": [
                    "csv_loading", "tsv_loading", "json_loading", "jsonl_loading",
                    "type_inference", "statistical_profiling", "correlation_analysis",
                    "outlier_detection", "viz_recommendation", "insight_generation",
                    "markdown_report", "json_report", "dataset_comparison",
                    "session_management", "quality_scoring",
                ],
                "supported_formats": list(DataLoader.SUPPORTED_FORMATS),
            }

    # ── Private Methods ──

    def _profile_column(self, name: str, values: List[Any], total: int) -> ColumnProfile:
        """Build complete profile for a single column."""
        non_null = [v for v in values if v is not None]
        missing = total - len(non_null)
        unique_vals = set(str(v) for v in non_null)

        col_type = TypeInferenceEngine.infer(name, values, total)

        profile = ColumnProfile(
            name=name,
            dtype=type(non_null[0]).__name__ if non_null else "NoneType",
            inferred_type=col_type,
            total_count=total,
            missing_count=missing,
            missing_pct=(missing / total * 100) if total > 0 else 0.0,
            unique_count=len(unique_vals),
            unique_pct=(len(unique_vals) / len(non_null) * 100) if non_null else 0.0,
        )

        if col_type == ColumnType.NUMERIC:
            nums = []
            for v in non_null:
                try:
                    nums.append(float(v))
                except (ValueError, TypeError):
                    pass
            if nums:
                profile.mean = self._stats.mean(nums)
                profile.median = self._stats.median(nums)
                profile.std = self._stats.std(nums)
                profile.min_val = min(nums)
                profile.max_val = max(nums)
                profile.q1 = self._stats.percentile(nums, 25)
                profile.q3 = self._stats.percentile(nums, 75)
                profile.iqr = profile.q3 - profile.q1
                profile.skewness = self._stats.skewness(nums)
                profile.kurtosis = self._stats.kurtosis(nums)
                profile.zero_count = sum(1 for x in nums if x == 0)
                profile.negative_count = sum(1 for x in nums if x < 0)
                outlier_idx = self._stats.detect_outliers_iqr(nums)
                profile.outlier_count = len(outlier_idx)
                if profile.outlier_count > 0:
                    profile.warnings.append(f"{profile.outlier_count} outliers detected (IQR method)")

        elif col_type in (ColumnType.CATEGORICAL, ColumnType.BOOLEAN):
            freq: Dict[str, int] = {}
            for v in non_null:
                s = str(v)
                freq[s] = freq.get(s, 0) + 1
            sorted_freq = sorted(freq.items(), key=lambda x: x[1], reverse=True)
            profile.top_values = sorted_freq[:10]
            profile.entropy = self._stats.entropy(list(freq.values()))

        elif col_type == ColumnType.TEXT:
            lengths = [len(str(v)) for v in non_null]
            if lengths:
                profile.avg_length = self._stats.mean([float(l) for l in lengths])
                profile.min_length = min(lengths)
                profile.max_length = max(lengths)

        # Warnings
        if profile.missing_pct > 50:
            profile.warnings.append(f"High missing rate: {profile.missing_pct:.1f}%")
        if profile.unique_count == 1:
            profile.warnings.append("Constant column — no variance")
        if col_type == ColumnType.CATEGORICAL and profile.unique_pct > 95:
            profile.warnings.append("Near-unique categorical — may be identifier")

        # Viz recommendations
        profile.recommended_viz = VizRecommender.recommend_univariate(profile)

        return profile

    def _compute_correlations(
        self,
        numeric_profiles: Dict[str, ColumnProfile],
        col_values: Dict[str, List[Any]],
    ) -> List[CorrelationResult]:
        """Compute pairwise correlations for numeric columns."""
        results = []
        names = list(numeric_profiles.keys())

        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a_name, b_name = names[i], names[j]
                a_vals = col_values[a_name]
                b_vals = col_values[b_name]

                # Aligned non-null pairs
                pairs = []
                for av, bv in zip(a_vals, b_vals):
                    if av is not None and bv is not None:
                        try:
                            pairs.append((float(av), float(bv)))
                        except (ValueError, TypeError):
                            pass

                if len(pairs) < 5:
                    continue

                xa = [p[0] for p in pairs]
                xb = [p[1] for p in pairs]

                pearson = self._stats.pearson_correlation(xa, xb)
                spearman = self._stats.spearman_correlation(xa, xb)

                strength = "none"
                if pearson is not None:
                    abs_p = abs(pearson)
                    if abs_p >= 0.7:
                        strength = "strong"
                    elif abs_p >= 0.4:
                        strength = "moderate"
                    elif abs_p >= 0.2:
                        strength = "weak"

                results.append(CorrelationResult(
                    column_a=a_name,
                    column_b=b_name,
                    pearson=round(pearson, 4) if pearson is not None else None,
                    spearman=round(spearman, 4) if spearman is not None else None,
                    strength=strength,
                ))

        return results

    def _compute_quality_score(
        self,
        profiles: Dict[str, ColumnProfile],
        dup_count: int,
        row_count: int,
    ) -> float:
        """Compute overall data quality score (0-100)."""
        if not profiles:
            return 0.0

        score = 100.0
        n_cols = len(profiles)

        # Missing penalty
        avg_missing = sum(p.missing_pct for p in profiles.values()) / n_cols
        score -= avg_missing * 0.5

        # Duplicate penalty
        if row_count > 0:
            dup_pct = dup_count / row_count * 100
            score -= dup_pct * 0.3

        # Constant columns penalty
        constant = sum(1 for p in profiles.values() if p.unique_count <= 1)
        score -= (constant / n_cols) * 15

        # Outlier penalty
        outlier_cols = sum(1 for p in profiles.values() if p.outlier_count > 0)
        score -= (outlier_cols / n_cols) * 5

        return max(0.0, min(100.0, score))

    @staticmethod
    def _score_to_level(score: float) -> DataQualityLevel:
        if score >= 95:
            return DataQualityLevel.EXCELLENT
        elif score >= 85:
            return DataQualityLevel.GOOD
        elif score >= 70:
            return DataQualityLevel.MODERATE
        elif score >= 50:
            return DataQualityLevel.POOR
        else:
            return DataQualityLevel.CRITICAL
