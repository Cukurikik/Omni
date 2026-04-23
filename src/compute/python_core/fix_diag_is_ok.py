import os
import glob
import re

TESTS_DIR = r'c:\Users\IKYY\Downloads\Omni\tests\integration'

test_files = glob.glob(os.path.join(TESTS_DIR, 'test_semester10_batch*.py'))
for f in test_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        
    modified = False

    # Find blocks of def test_...diagnostics():
    parts = re.split(r'(def\s+test_\w*diagnostics\w*\(\):)', content)
    
    for i in range(1, len(parts), 2):
        func_def = parts[i]
        func_body = parts[i+1]
        
        # In the diagnostics test body, replace variable.is_ok()
        new_body, count = re.subn(r'assert\s+([a-zA-Z0-9_]+)\.is_ok\(\)', r'assert \1["status"] == "operational"', func_body)
        if count > 0:
            parts[i+1] = new_body
            modified = True
            
        new_body, count2 = re.subn(r'assert\s+engine\.diagnostics\(\)\.is_ok\(\)', r'assert engine.diagnostics()["status"] == "operational"', parts[i+1])
        if count2 > 0:
            parts[i+1] = new_body
            modified = True

    if modified:
        content = "".join(parts)
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

print("Sweeps completed.")
