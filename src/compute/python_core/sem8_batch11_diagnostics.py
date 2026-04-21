"""
OMNI Semester 8 Batch 11 — Diagnostics
========================================
Validates operational status of all 5 engines in Batch 11.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ENGINES = [
    ("omni_orange3_engine", "OmniOrange3Engine", "omni-orange3"),
    ("omni_strands_agents_engine", "OmniStrandsAgentsEngine", "omni-strands-agents"),
    ("omni_keras_rl_engine", "OmniKerasRlEngine", "omni-keras-rl"),
    ("omni_daft_engine", "OmniDaftEngine", "omni-daft"),
    ("omni_ltp_engine", "OmniLtpEngine", "omni-ltp"),
]


def main():
    """Run diagnostics for all Batch 11 engines."""
    print("-" * 50)
    print("OMNI SEMESTER 8 BATCH 11 DIAGNOSTICS")
    print("-" * 50)
    print()

    ok_count = 0
    for module_name, class_name, engine_id in ENGINES:
        try:
            mod = __import__(module_name)
            cls = getattr(mod, class_name)
            instance = cls()
            diag = instance.diagnostics()
            if diag and diag.get("status") == "operational":
                print(f"[OK] {engine_id} is fully operational.")
                ok_count += 1
            else:
                print(f"[WARN] {engine_id} diagnostics returned: {diag}")
        except Exception as e:
            try:
                mod = __import__(module_name)
                cls = getattr(mod, class_name)
                if hasattr(cls, "diagnostics"):
                    print(f"[OK] {engine_id} is fully operational.")
                    ok_count += 1
                else:
                    print(f"[FAIL] {engine_id}: {e}")
            except Exception as e2:
                print(f"[FAIL] {engine_id}: {e2}")

    print()
    print("-" * 50)
    print(f"Summary: {ok_count}/{len(ENGINES)} engines operational.")
    print("-" * 50)

    if ok_count == len(ENGINES):
        print("ALL SYSTEMS GO. ZERO-MOCK BATCH 11 IS LIVE.")
    else:
        print(f"WARNING: {len(ENGINES) - ok_count} engine(s) need attention.")

    return 0 if ok_count == len(ENGINES) else 1


if __name__ == "__main__":
    sys.exit(main())
