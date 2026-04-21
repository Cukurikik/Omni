"""
OMNI Bridge Layer — Python Package Initializer.

Provides cross-layer communication bridges following OMNI Domain Segregation rules.
UI -> Bridge -> Compute (never direct UI -> Compute imports).
"""

from typing import Dict, Any


def get_bridge_manifest() -> Dict[str, Any]:
    """Return metadata about available bridge modules."""
    return {
        "bridges": {
            "compute_bridge": {"file": "compute_bridge.py", "lang": "Python", "connects": "UI <-> Compute"},
            "domain_bridge": {"file": "domain_bridge.ts", "lang": "TypeScript", "connects": "UI <-> Domain"},
            "network_bridge": {"file": "network_bridge.go", "lang": "Go", "connects": "UI <-> Network"},
            "system_bridge": {"file": "system_bridge.rs", "lang": "Rust", "connects": "Compute <-> System"},
            "ui_bridge": {"file": "ui_bridge.dart", "lang": "Dart", "connects": "Mobile <-> UI"},
        },
        "total": 5,
        "layer": "bridge",
    }


__all__ = ["get_bridge_manifest"]
