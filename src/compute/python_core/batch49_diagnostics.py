import sys
import os

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.compute.python_core.system.omni_ltsf_linear_engine import OmniLtsfLinearEngine
from src.compute.python_core.system.omni_kuberay_engine import OmniKubeRayEngine
from src.compute.python_core.system.omni_autoformer_engine import OmniAutoformerEngine
from src.compute.python_core.system.omni_recsys_ads_engine import OmniRecSysAdsEngine
from src.compute.python_core.system.omni_graphormer_engine import OmniGraphormerEngine

def run_diagnostics():
    print("========================================================================")
    print("  BATCH 49 -- SEMESTER 7 DIAGNOSTICS (BATCH 19)")
    print("========================================================================")
    
    engines = [
        ("OmniLtsfLinearEngine", OmniLtsfLinearEngine),
        ("OmniKubeRayEngine", OmniKubeRayEngine),
        ("OmniAutoformerEngine", OmniAutoformerEngine),
        ("OmniRecSysAdsEngine", OmniRecSysAdsEngine),
        ("OmniGraphormerEngine", OmniGraphormerEngine)
    ]
    
    results = []
    
    for name, engine_cls in engines:
        try:
            print(f"  [LOAD] {name}...", end="")
            engine_instance = engine_cls()
            status = engine_instance.get_system_status()
            
            if status.get("status") == "success" and status.get("state") == "operational":
                print(" OK -- OPERATIONAL")
                results.append((name, "OK"))
            else:
                print(" FAILED -- BAD STATUS")
                results.append((name, "FAILED"))
        except Exception as e:
            print(f" ERROR -- {str(e)}")
            results.append((name, "FAILED"))
            
    # Print summary
    successful = len([r for r in results if r[1] == "OK"])
    failed = len(results) - successful
    
    print("========================================================================")
    print(f"  RESULTS: {successful}/{len(results)} OPERATIONAL  | {failed} FAILED")
    print("========================================================================")
    for name, state in results:
        pad_name = name.ljust(35)
        print(f"  [{state}] {pad_name} v1.0.0    caps=3")
    print("========================================================================")

if __name__ == "__main__":
    run_diagnostics()
