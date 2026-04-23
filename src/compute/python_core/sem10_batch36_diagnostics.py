import sys
from omni_vscode_shortcuts_engine import OmniVscodeShortcutsEngine
from omni_git_analyzer_engine import OmniGitAnalyzerEngine
from omni_learnlang_engine import OmniLearnlangEngine
from omni_gam3du_engine import OmniGam3duEngine
from omni_apis_engine import OmniAPIsEngine

def run_diagnostics():
    print("========================================================================")
    print("  BATCH 36 -- SEMESTER 10 DIAGNOSTICS")
    print("========================================================================\n")
    
    engines = [
        OmniVscodeShortcutsEngine(),
        OmniGitAnalyzerEngine(),
        OmniLearnlangEngine(),
        OmniGam3duEngine(),
        OmniAPIsEngine()
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
