import sys
from omni_go_start_engine import OmniGoStartEngine
from omni_vid_game_console_management_engine import OmniVidGameConsoleManagementEngine
from omni_hunger_games_search_engine import OmniHungerGamesSearchEngine
from omni_course_dev_engine import OmniCourseDevEngine
from omni_development_rules_engine import OmniDevelopmentRulesEngine

def run_diagnostics():
    print("========================================================================")
    print("  BATCH 38 -- SEMESTER 10 DIAGNOSTICS")
    print("========================================================================\n")
    
    engines = [
        OmniGoStartEngine(),
        OmniVidGameConsoleManagementEngine(),
        OmniHungerGamesSearchEngine(),
        OmniCourseDevEngine(),
        OmniDevelopmentRulesEngine()
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
