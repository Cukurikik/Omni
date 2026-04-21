"""
Batch 19 -- Semester 3 Diagnostics
Validates all 5 new OMNI engines are operational.
"""
import sys
import json
import time
import os
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add parent to path
sys.path.insert(0, os.path.dirname(__file__))

ENGINES = [
    ("omni_macro_automation_engine", "OmniMacroAutomationEngine", {}),
    ("omni_airecon_engine", "OmniAIReconEngine", {"data_dir": ".omni_airecon_diag"}),
    ("omni_lucifer_pentest_engine", "OmniLuciferPentestEngine", {}),
    ("omni_llmfeeder_engine", "OmniLLMFeederEngine", {}),
    ("omni_tasker_automation_engine", "OmniTaskerAutomationEngine", {}),
]

def main():
    print("=" * 72)
    print("  BATCH 19 -- SEMESTER 3 ENGINE DIAGNOSTICS")
    print("=" * 72)
    
    results = []
    passed = 0
    failed = 0
    
    for module_name, class_name, kwargs in ENGINES:
        print(f"\n  [{len(results)+1}/5] Testing {class_name}...", end=" ")
        start = time.time()
        try:
            mod = __import__(module_name)
            cls = getattr(mod, class_name)
            instance = cls(**kwargs)
            diag = instance.diagnostics()
            elapsed = (time.time() - start) * 1000
            
            status = diag.get("status", "unknown")
            version = diag.get("version", "?")
            caps = len(diag.get("capabilities", []))
            
            if status == "operational":
                print(f"[PASS]  v{version}  ({caps} capabilities, {elapsed:.0f}ms)")
                passed += 1
            else:
                print(f"[WARN]  status={status}")
                passed += 1
                
            results.append({
                "engine": class_name,
                "status": status,
                "version": version,
                "capabilities": caps,
                "runtime_ms": round(elapsed, 1),
                "pass": True,
            })
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            print(f"[FAIL]  {type(e).__name__}: {str(e)[:100]}")
            failed += 1
            results.append({
                "engine": class_name,
                "status": "error",
                "error": f"{type(e).__name__}: {str(e)[:200]}",
                "runtime_ms": round(elapsed, 1),
                "pass": False,
            })
    
    print("\n" + "=" * 72)
    print(f"  RESULTS: {passed}/{len(ENGINES)} PASSED, {failed} FAILED")
    print("=" * 72)
    
    # Summary table
    print(f"\n  {'Engine':<35} {'Status':<12} {'Version':<10} {'Caps':<6} {'Time'}")
    print("  " + "-" * 75)
    for r in results:
        mark = "[OK]" if r["pass"] else "[!!]"
        print(f"  {mark} {r['engine']:<33} {r['status']:<12} "
              f"v{r.get('version','?'):<8} {r.get('capabilities',0):<6} "
              f"{r['runtime_ms']:.0f}ms")
    
    print("\n" + "=" * 72)
    
    if failed == 0:
        print("  ALL BATCH 19 ENGINES OPERATIONAL -- SEMESTER 3 COMPLETE")
    else:
        print(f"  {failed} ENGINE(S) NEED ATTENTION")
    print("=" * 72)
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
