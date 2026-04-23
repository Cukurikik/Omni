import sys
from omni_dalhousie_sdc_engine import OmniDalhousieSDCEngine
from omni_calculator_app_engine import OmniCalculatorAppEngine
from omni_adhd_wordsearch_engine import OmniADHDWordSearchEngine
from omni_software_product_management_engine import OmniSoftwareProductManagementEngine
from omni_code_auditor_engine import OmniCodeAuditorEngine

def run_diagnostics():
    engines = [
        OmniDalhousieSDCEngine(),
        OmniCalculatorAppEngine(),
        OmniADHDWordSearchEngine(),
        OmniSoftwareProductManagementEngine(),
        OmniCodeAuditorEngine()
    ]
    
    print("========================================================================")
    print("  BATCH 44 -- SEMESTER 10 DIAGNOSTICS")
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
