import sys
import os

# Ensure the project root is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.compute.python_core.system.omni_manga_ocr_engine import OmniMangaOCREngine
from src.compute.python_core.system.omni_gluon_nlp_engine import OmniGluonNLPEngine
from src.compute.python_core.system.omni_lanenet_engine import OmniLaneNetEngine
from src.compute.python_core.system.omni_libmtl_engine import OmniLibMTLEngine
from src.compute.python_core.system.omni_comic_translate_engine import OmniComicTranslateEngine

def run_diagnostics():
    print("========================================================================")
    print("  BATCH 47 -- SEMESTER 7 DIAGNOSTICS (BATCH 17)")
    print("========================================================================")
    
    engines = [
        ("OmniMangaOCREngine", OmniMangaOCREngine),
        ("OmniGluonNLPEngine", OmniGluonNLPEngine),
        ("OmniLaneNetEngine", OmniLaneNetEngine),
        ("OmniLibMTLEngine", OmniLibMTLEngine),
        ("OmniComicTranslateEngine", OmniComicTranslateEngine)
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
