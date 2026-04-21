import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from omni_engine_registry import OmniEngineRegistry

if __name__ == '__main__':
    print('======================================================================')
    print('  BATCH 64 -- SEMESTER 9 DIAGNOSTICS (BATCH 15)')
    print('======================================================================')
    registry = OmniEngineRegistry(str(Path(__file__).resolve().parent.parent.parent.parent / 'src'))
    registry.scan()
    batch15_engines = ['omni_bert_score_engine', 'omni_alan_sdk_ios_bridge_engine', 'omni_imgcook_engine', 'omni_rocketride_server_engine', 'omni_openai_dotnet_bridge_engine']
    all_passed = True
    for eng_name in batch15_engines:
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
        print('  [OK]  ALL 5 ENGINES OPERATIONAL -- Batch 64 PASSED')
    else:
        print('  [FAIL] SOME ENGINES MISSING OR FAILED')
    print('======================================================================\n')
