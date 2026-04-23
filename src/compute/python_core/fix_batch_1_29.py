import os
import re

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    modified = False

    # 1. Remove bespoke Ok/Err classes
    bespoke_ok_err_pattern = re.compile(
        r'# Monadic Result Wrapper\nclass Ok:.*?(?=class |def |$)', 
        re.DOTALL
    )
    if bespoke_ok_err_pattern.search(content):
        content = bespoke_ok_err_pattern.sub('', content)
        modified = True
        
    bespoke_ok_err_pattern2 = re.compile(
        r'class Ok:\n.*?(?=\nclass Err:|\n\w|$)class Err:\n.*?(?=\n\n|\n\w|$)',
        re.DOTALL
    )
    if bespoke_ok_err_pattern2.search(content):
        content = bespoke_ok_err_pattern2.sub('', content)
        modified = True

    # 2. Remove bespoke @dataclass Result
    bespoke_result_pattern = re.compile(
        r'@dataclass\nclass Result:\n    is_ok: bool\n.*?def Err\(.*?\).*?return Result\(.*?\)\n',
        re.DOTALL
    )
    if bespoke_result_pattern.search(content):
        content = bespoke_result_pattern.sub('', content)
        modified = True

    class_result_pattern = re.compile(
        r'class Result:\n    def __init__.*?def Err\(.*?\).*?return Result\(.*?\)\n',
        re.DOTALL
    )
    if class_result_pattern.search(content):
        content = class_result_pattern.sub('', content)
        modified = True

    # 3. Inject standard import if we removed bespoke ones or if it uses Result but lacks import
    has_custom = modified
    lacks_import = 'from src.compute.python_core.omni_base_engine import Result, Ok, Err' not in content
    uses_result = 'Result' in content or 'Ok(' in content or 'Err(' in content
    
    if (has_custom or uses_result) and lacks_import:
        # insert right after imports
        import_block_end = re.search(r'^(import|from) .*?(\n\n|$)', content, re.MULTILINE | re.DOTALL)
        if import_block_end:
            content = content[:import_block_end.end()] + "from src.compute.python_core.omni_base_engine import Result, Ok, Err\n" + content[import_block_end.end():]
        else:
            # no imports found, insert at top (after docstrings)
            docstring_end = re.search(r'^""".*?"""\n', content, re.DOTALL)
            if docstring_end:
                content = content[:docstring_end.end()] + "\nfrom src.compute.python_core.omni_base_engine import Result, Ok, Err\n" + content[docstring_end.end():]
            else:
                content = "from src.compute.python_core.omni_base_engine import Result, Ok, Err\n\n" + content
        modified = True

    # 4. Standardize diagnostics() returning Result.Ok("...")
    diag_pattern = re.compile(
        r'def diagnostics\(.*?\).*?(?:-> Result|-> .*?)?:\n\s+return Result\.Ok\(["\'](.*?)(?:: OK| OK|)["\']\)',
        re.DOTALL
    )
    def diag_repl(m):
        engine_name = m.group(1).split(":")[0].strip()
        if not engine_name.startswith("Omni"):
            engine_name = "OmniEngine"
        return f'def diagnostics() -> Dict[str, Any]:\n        return {{\n            "engine": "{engine_name}",\n            "status": "operational",\n            "monadic_enforcement": True\n        }}'

    new_content, count = diag_pattern.subn(diag_repl, content)
    if count > 0:
        content = new_content
        modified = True

    # Fix generic typing for Dict, Any if diagnostics was fixed and lacks typing
    if count > 0 and 'from typing import ' not in content and 'import typing' not in content:
        content = "from typing import Dict, Any, List, Optional\n" + content
    elif count > 0 and 'Dict' not in content:
        content = content.replace('from typing import ', 'from typing import Dict, Any, ')

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

import glob
count = 0
files = glob.glob(os.path.join(TARGET_DIR, 'omni_*_engine.py'))
for f in files:
    try:
        if process_file(f):
            count += 1
            print(f"Fixed: {os.path.basename(f)}")
    except Exception as e:
        print(f"Error processing {os.path.basename(f)}: {e}")

print(f"Total engines standardized: {count}")
