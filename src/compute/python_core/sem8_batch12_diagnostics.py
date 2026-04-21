"""
Semester 8 Batch 12 — Diagnostics Runner

Performs health-check diagnostics on all 5 Batch 12 engines and reports
their operational status in a unified output.
"""

import sys
import json

from omni_zenml_engine import OmniZenMLEngine
from omni_sahi_engine import OmniSAHIEngine
from omni_augmentor_engine import OmniAugmentorEngine
from omni_ai_datasci_team_engine import OmniAIDataSciTeamEngine
from omni_synapse_ml_engine import OmniSynapseMLEngine


def run_diagnostics() -> dict:
    """Execute diagnostics on all Batch 12 engines.

    Returns:
        Dictionary with per-engine diagnostics and overall status.
    """
    engines = {
        "OmniZenMLEngine": OmniZenMLEngine(),
        "OmniSAHIEngine": OmniSAHIEngine(),
        "OmniAugmentorEngine": OmniAugmentorEngine(),
        "OmniAIDataSciTeamEngine": OmniAIDataSciTeamEngine(),
        "OmniSynapseMLEngine": OmniSynapseMLEngine(),
    }

    report = {
        "batch": "Semester 8 — Batch 12",
        "engines": {},
        "total": len(engines),
        "healthy": 0,
        "unhealthy": 0,
    }

    for name, engine in engines.items():
        diag = engine.diagnostics()
        status = diag.get("status", "unknown")
        report["engines"][name] = diag
        if status in ("operational", "active"):
            report["healthy"] += 1
        else:
            report["unhealthy"] += 1

    report["overall_status"] = "ALL_HEALTHY" if report["unhealthy"] == 0 else "DEGRADED"
    return report


if __name__ == "__main__":
    result = run_diagnostics()
    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result["overall_status"] == "ALL_HEALTHY" else 1)
