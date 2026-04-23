import sys
from omni_mindnote_engine import OmniMindnoteEngine
from omni_comp_tech_list_engine import OmniCompTechListEngine
from omni_nge2_engine import OmniNGE2Engine
from omni_integration_test_engine import OmniIntegrationTestEngine
from omni_disaster_response_engine import OmniDisasterResponseEngine

def run_diagnostics():
    print("========================================================================")
    print("  BATCH 37 -- SEMESTER 10 DIAGNOSTICS")
    print("========================================================================\n")
    
    engines = [
        OmniMindnoteEngine(),
        OmniCompTechListEngine(),
        OmniNGE2Engine(),
        OmniIntegrationTestEngine(),
        OmniDisasterResponseEngine()
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
