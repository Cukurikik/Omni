import os
import glob
import re

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'
TESTS_DIR = r'c:\Users\IKYY\Downloads\Omni\tests\integration'

# 1. Fix Result.Ok -> Ok, Result.Err -> Err in engines
files = glob.glob(os.path.join(TARGET_DIR, 'omni_*_engine.py'))
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    modified = False
    new_content, count = re.subn(r'Result\.Ok\(', r'Ok(', content)
    if count > 0:
        content = new_content
        modified = True
        
    new_content, count2 = re.subn(r'Result\.Err\(', r'Err(', content)
    if count2 > 0:
        content = new_content
        modified = True

    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

# 2. Fix tests expectations around Ok/Err imports and diagnostics
test_files = glob.glob(os.path.join(TESTS_DIR, 'test_semester10_batch*.py'))
for f in test_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        
    modified = False
    
    # Fix Ok as OkXXX imports
    new_content, count = re.subn(r',\s*Ok\s+as\s+\w+', '', content)
    if count > 0:
        content = new_content
        modified = True
        
    new_content, count2 = re.subn(r',\s*Err\s+as\s+\w+', '', content)
    if count2 > 0:
        content = new_content
        modified = True

    # Fix diag.is_ok() -> diag["status"] == "operational" (or similar handling)
    # Usually: assert diag.is_ok()
    new_content, count3 = re.subn(r'assert\s+diag\.is_ok\(\)(?:\s+is\s+True|)', r'assert diag["status"] == "operational"', content)
    if count3 > 0:
        content = new_content
        modified = True
        
    # Usually: diag = engine.diagnostics().unwrap()
    new_content, count4 = re.subn(r'diagnostics\(\)\.unwrap\(\)', r'diagnostics()', content)
    if count4 > 0:
        content = new_content
        modified = True
        
    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

print("Sweeps completed.")
