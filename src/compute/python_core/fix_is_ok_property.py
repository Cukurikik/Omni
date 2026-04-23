import os
import glob
import re

TESTS_DIR = r'c:\Users\IKYY\Downloads\Omni\tests\integration'

test_files = glob.glob(os.path.join(TESTS_DIR, 'test_semester10_batch*.py'))
for f in test_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        
    modified = False

    # Replace .is_ok is True with .is_ok()
    new_content, count = re.subn(r'\.is_ok\s+is\s+True', r'.is_ok()', content)
    if count > 0:
        content = new_content
        modified = True

    # Replace .is_ok is False with not .is_ok()
    # E.g., assert res.is_ok is False -> assert not res.is_ok()
    new_content, count2 = re.subn(r'assert\s+([a-zA-Z0-9_]+)\.is_ok\s+is\s+False', r'assert not \1.is_ok()', content)
    if count2 > 0:
        content = new_content
        modified = True

    # Replace .is_ok(not followed by '(') with .is_ok()
    # Lookahead for not '('
    new_content, count3 = re.subn(r'\.is_ok(?!\()', r'.is_ok()', content)
    if count3 > 0:
        content = new_content
        modified = True

    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

print("Sweeps completed.")
