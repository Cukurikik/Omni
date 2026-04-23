import sys
from omni_dh_tech_engine import OmniDHTechEngine
from omni_breakbase_frontend_engine import OmniBreakbaseFrontendEngine
from omni_technical_hub_engine import OmniTechnicalHubEngine
from omni_kwaliteitsaanpak_engine import OmniKwaliteitsaanpakEngine
from omni_sboannotator_engine import OmniSBOannotatorEngine

def run_diagnostics():
    print("========================================================================")
    print("  BATCH 35 -- SEMESTER 10 DIAGNOSTICS")
    print("========================================================================\n")
    
    engines = [
        OmniDHTechEngine(),
        OmniBreakbaseFrontendEngine(),
        OmniTechnicalHubEngine(),
        OmniKwaliteitsaanpakEngine(),
        OmniSBOannotatorEngine()
    ]
    
    passed = 0
    for e in engines:
        diag = e.diagnostics()
        if diag.get("status") == "operational":
            print(f"  [LOAD] {diag.get('engine')}... OK -- OPERATIONAL")
            passed += 1
        else:
            print(f"  [LOAD] {e.__class__.__name__}... FAILED")
            
    print("\n========================================================================")
    print(f"  RESULTS: {passed}/5 OPERATIONAL  | {5 - passed} FAILED")
    print("========================================================================")
    
    for e in engines:
        diag = e.diagnostics()
        print(f"  [{'OK' if diag.get('status') == 'operational' else 'FAIL'}] {diag.get('engine').ljust(35)} v{diag.get('version').ljust(8)} caps=2")
    print("========================================================================")

if __name__ == "__main__":
    run_diagnostics()
