"""OmniHardwareTelemetryBaselineEngine — Spec Baseline Evaluation.

Inspired by nvb-g/DashComputer: a software utility to analyze and
dashboard operating telemetry of a PC including hardware specs,
network, and operational stats.

Algorithmic Primitive:
    Compare live system hardware telemetry against declared minimum
    operational baselines. Report compliance gaps systematically.
"""
from __future__ import annotations
import sys, os
from src.compute.python_core.omni_base_engine import Result, Ok, Err
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))


class OmniHardwareTelemetryBaselineEngine:
    """Production-grade hardware specifications verification engine."""

    @staticmethod
    def diagnostics() -> dict:
        """Return engine metadata for OMNI ecosystem health checks."""
        return {
            "engine": "OmniHardwareTelemetryBaselineEngine",
            "version": "1.0.0",
            "primitive": "hardware_baseline_compliance_verification",
            "monadic_enforcement": True,
            "source_repo": "nvb-g/DashComputer",
        }

    @staticmethod
    def evaluate_against_baseline(
        telemetry: dict[str, float | int],
        baseline: dict[str, float | int],
    ) -> Result:
        """Evaluate captured system telemetry against hard baselines.

        Args:
            telemetry: Current stats, e.g., {'ram_gb': 16, 'cpu_cores': 8}.
            baseline: Minimum required, e.g., {'ram_gb': 12, 'cpu_cores': 4}.

        Returns:
            Result[dict, Exception]: dict detailing compliance, gaps,
            and an overall boolean 'compliant'.
        """
        if not isinstance(telemetry, dict) or not isinstance(baseline, dict):
            return Err(Exception("telemetry and baseline must be dictionaries"))

        compliant = True
        evaluation: dict[str, dict] = {}
        missing_keys: list[str] = []

        for req_key, req_val in baseline.items():
            if not isinstance(req_val, (int, float)):
                return Err(Exception(f"Baseline value for '{req_key}' must be numeric"))

            if req_key not in telemetry:
                missing_keys.append(req_key)
                compliant = False
                continue
                
            actual_val = telemetry[req_key]
            if not isinstance(actual_val, (int, float)):
                return Err(Exception(f"Telemetry value for '{req_key}' must be numeric"))

            is_pass = actual_val >= req_val
            gap = round(req_val - actual_val, 2) if not is_pass else 0.0
            
            if not is_pass:
                compliant = False

            evaluation[req_key] = {
                "required": req_val,
                "actual": actual_val,
                "passed": is_pass,
                "deficit": gap,
            }

        if missing_keys:
            return Err(Exception(f"Telemetry missing required keys for baseline check: {', '.join(missing_keys)}"))

        return Ok({
            "is_compliant": compliant,
            "evaluations": evaluation,
            "total_specs_checked": len(baseline),
        })

    @staticmethod
    def compute_network_quality_score(
        ping_ms: float,
        download_mbps: float,
        upload_mbps: float,
    ) -> Result:
        """Compute an arbitrary abstract network quality score (0-100).
        
        Args:
            ping_ms: Lower is better.
            download_mbps: Higher is better.
            upload_mbps: Higher is better.
            
        Returns:
            Result[float, Exception]: A quality score metric.
        """
        if ping_ms < 0 or download_mbps < 0 or upload_mbps < 0:
            return Err(Exception("Metrics cannot be negative"))
            
        # Simplistic network scoring primitive
        ping_score = max(0.0, 100 - (ping_ms * 0.5))
        dl_score = min(100.0, download_mbps)
        ul_score = min(100.0, (upload_mbps * 2.5))
        
        composite = (ping_score * 0.4) + (dl_score * 0.4) + (ul_score * 0.2)
        return Ok(round(composite, 2))
