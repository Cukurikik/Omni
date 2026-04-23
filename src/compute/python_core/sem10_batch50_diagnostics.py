import sys
from omni_frequency_counter_engine import OmniFrequencyCounterEngine
from omni_prime_plus_preprocessor_engine import OmniPrimePlusPreprocessorEngine
from omni_protein_dj_engine import OmniProteinDJEngine
from omni_fibonacci_analysis_engine import OmniFibonacciAnalysisEngine
from omni_shadow_map_engine import OmniShadowMapEngine

def run_diagnostics():
    engines = [
        OmniFrequencyCounterEngine(),
        OmniPrimePlusPreprocessorEngine(),
        OmniProteinDJEngine(),
        OmniFibonacciAnalysisEngine(),
        OmniShadowMapEngine()
    ]
    
    print("========================================================================")
    print("  BATCH 50 -- SEMESTER 10 DIAGNOSTICS")
    print("========================================================================\n")
    
    all_ok = True
    results = []
    
    for eng in engines:
        name = eng.__class__.__name__
        try:
            diag = eng.diagnostics()
            if diag.get("status") == "operational":
                print(f"  [LOAD] {name}... OK -- OPERATIONAL")
                results.append((name, diag.get("version"), len(diag.get("capabilities", []))))
            else:
                print(f"  [LOAD] {name}... FAILED STATUS")
                all_ok = False
        except Exception as e:
            print(f"  [LOAD] {name}... ERROR: {e}")
            all_ok = False
            
    print("\n========================================================================")
    if all_ok:
        print(f"  RESULTS: {len(engines)}/{len(engines)} OPERATIONAL  | 0 FAILED")
    else:
        print("  RESULTS: SYSTEM INSTABILITY DETECTED")
    print("========================================================================")
    
    for r in results:
        print(f"  [OK] {r[0].ljust(40)} v{r[1]}    caps={r[2]}")
    print("========================================================================")
    
    if not all_ok:
        sys.exit(1)

if __name__ == "__main__":
    run_diagnostics()
