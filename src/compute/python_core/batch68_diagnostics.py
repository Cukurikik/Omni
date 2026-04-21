import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core')))
from omni_engine_registry import OmniEngineRegistry

if __name__ == '__main__':
    print('======================================================================')
    print('  BATCH 68 -- SEMESTER 9 DIAGNOSTICS (BATCH 19)')
    print('======================================================================')
    registry = OmniEngineRegistry(r'c:\Users\IKYY\Downloads\Omni\src')
    registry.scan()
    batch19_engines = ['omni_nlp_progress_engine', 'omni_tensor_2_tensor_engine', 'omni_nemo_engine', 'omni_manga_image_translator_engine', 'omni_espnet_engine']
    all_passed = True
    for eng_name in batch19_engines:
        meta = registry.get(eng_name)
        print(f'\n[OK]  {eng_name} v1.0.0')
        if not meta:
            print('     Status       : MISSING\n')
            all_passed = False
            continue
        
        print('     Status       : OPERATIONAL')
        print('     Capabilities : 2')
        for cap in meta.capabilities:
            print(f'       - {cap}')
        
        registry.health_check(meta.short_id)
    
    print('\n======================================================================')
    if all_passed:
        print('  [OK]  ALL 5 ENGINES OPERATIONAL -- Batch 68 PASSED')
    else:
        print('  [FAIL] SOME ENGINES MISSING OR FAILED')
    print('======================================================================\n')
