import os
import glob
import re

TESTS_DIR = r'c:\Users\IKYY\Downloads\Omni\tests\integration'

test_files = glob.glob(os.path.join(TESTS_DIR, 'test_semester10_batch*.py'))
for f in test_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        
    modified = False
    
    new_content, count = re.subn(r'engine\.diagnostics\(\)\.is_ok\(\)', r'engine.diagnostics()["status"] == "operational"', content)
    if count > 0:
        content = new_content
        modified = True

    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

print("Sweeps completed.")
