import sys
from omni_alexa_emergency_system_engine import OmniAlexaEmergencySystemEngine
from omni_autumn_mcp_engine import OmniAutumnMCPEngine
from omni_brick_master_vr_engine import OmniBrickMasterVREngine
from omni_dev_task_flow_engine import OmniDevTaskFlowEngine
from omni_messaging_patterns_engine import OmniMessagingPatternsEngine

def run_diagnostics():
    engines = [
        OmniAlexaEmergencySystemEngine(),
        OmniAutumnMCPEngine(),
        OmniBrickMasterVREngine(),
        OmniDevTaskFlowEngine(),
        OmniMessagingPatternsEngine()
    ]
    
    print("========================================================================")
    print("  BATCH 41 -- SEMESTER 10 DIAGNOSTICS")
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
