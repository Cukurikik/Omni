import os
import re
import glob

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'

files = glob.glob(os.path.join(TARGET_DIR, 'omni_*_engine.py'))
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    modified = False

    # Fix syntax error where 'from' follows immediately after a word
    new_content, count = re.subn(r'([A-Za-z0-9_\]\'\"])(from src\.compute\.python_core\.omni_base_engine import Result, Ok, Err)', r'\1\n\2', content)
    if count > 0:
        content = new_content
        modified = True

    # Fix indentation errors: leftover 'def unwrap(self) -> Any:' or 'raise self.error' at the end of the file
    leftover_pattern = re.compile(r'\s*def unwrap\(self\).*?(?:\n\s*return.*?(?:\n|$)|raise self.*?(?:\n|$))', re.DOTALL)
    new_content, count2 = leftover_pattern.subn('', content)
    if count2 > 0:
        content = new_content
        modified = True

    leftover_pattern2 = re.compile(r'\s*class Err:\n\s*def __init__.*?(?=\n\n|$)', re.DOTALL)
    new_content, count3 = leftover_pattern2.subn('', content)
    if count3 > 0:
        content = new_content
        modified = True
        
    leftover_pattern3 = re.compile(r'\s*class Ok:\n\s*def __init__.*?(?=\n\n|$)', re.DOTALL)
    new_content, count4 = leftover_pattern3.subn('', content)
    if count4 > 0:
        content = new_content
        modified = True

    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Fixed formatting in {os.path.basename(f)}")

