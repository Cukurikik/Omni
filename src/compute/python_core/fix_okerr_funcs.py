import os
import glob
import re

TESTS_DIR = r'c:\Users\IKYY\Downloads\Omni\tests\integration'

test_files = glob.glob(os.path.join(TESTS_DIR, 'test_semester10_batch*.py'))
for f in test_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        
    modified = False
    
    new_content, count = re.subn(r'isinstance\(([^,]+),\s*Ok\)', r'\1.is_ok()', content)
    if count > 0:
        content = new_content
        modified = True

    new_content, count2 = re.subn(r'isinstance\(([^,]+),\s*Err\)', r'not \1.is_ok()', content)
    if count2 > 0:
        content = new_content
        modified = True
        
    new_content, count3 = re.subn(r'type\(([^)]+)\)\s*is\s*Ok', r'\1.is_ok()', content)
    if count3 > 0:
        content = new_content
        modified = True

    new_content, count4 = re.subn(r'type\(([^)]+)\)\s*is\s*Err', r'not \1.is_ok()', content)
    if count4 > 0:
        content = new_content
        modified = True
        
    # Sometimes it might be things like ssert isinstance(res, Ok) and ...
    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

print("Sweeps completed.")
