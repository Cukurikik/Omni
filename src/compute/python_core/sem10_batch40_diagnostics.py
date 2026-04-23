import sys
from omni_regex_parser_engine import OmniRegexParserEngine
from omni_blog_archive_engine import OmniBlogArchiveEngine
from omni_swe_lecture_notes_engine import OmniSWELectureNotesEngine
from omni_bus_ticket_reservation_engine import OmniBusTicketReservationEngine
from omni_data_flow_diagram_engine import OmniDataFlowDiagramEngine

def run_diagnostics():
    engines = [
        OmniRegexParserEngine(),
        OmniBlogArchiveEngine(),
        OmniSWELectureNotesEngine(),
        OmniBusTicketReservationEngine(),
        OmniDataFlowDiagramEngine()
    ]
    
    print("========================================================================")
    print("  BATCH 40 -- SEMESTER 10 DIAGNOSTICS")
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
