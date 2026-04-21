import sys
import os

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.compute.python_core.system.omni_image_denoising_engine import OmniImageDenoisingEngine
from src.compute.python_core.system.omni_easylm_engine import OmniEasyLMEngine
from src.compute.python_core.system.omni_deep_tracking_engine import OmniDeepTrackingEngine
from src.compute.python_core.system.omni_simclr_engine import OmniSimCLREngine
from src.compute.python_core.system.omni_kompute_engine import OmniKomputeEngine

def run_diagnostics():
    print("========================================================================")
    print("  BATCH 48 -- SEMESTER 7 DIAGNOSTICS (BATCH 18)")
    print("========================================================================")
    
    engines = [
        ("OmniImageDenoisingEngine", OmniImageDenoisingEngine),
        ("OmniEasyLMEngine", OmniEasyLMEngine),
        ("OmniDeepTrackingEngine", OmniDeepTrackingEngine),
        ("OmniSimCLREngine", OmniSimCLREngine),
        ("OmniKomputeEngine", OmniKomputeEngine)
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
