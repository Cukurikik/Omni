import os
import glob
import re

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'

files = glob.glob(os.path.join(TARGET_DIR, 'omni_*_engine.py'))
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        
    modified = False
    
    new_content, count = re.subn(r'isinstance\(([^,]+),\s*Ok\)', r'\1.is_ok()', content)
    if count > 0:
        content = new_content
        modified = True

    new_content, count2 = re.subn(r'isinstance\(([^,]+),\s*Err\)', r'(not \1.is_ok())', content)
    if count2 > 0:
        content = new_content
        modified = True
        
    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

print("Sweeps completed.")
