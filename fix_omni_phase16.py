import os
import re

OMNI_ROOT = r"c:\Users\IKYY\Downloads\Omni\src"
fixes_applied = 0
files_fixed = 0

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except:
        return None

def write_file(path, content):
    try:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        return True
    except:
        return False

def fix_all_files():
    global fixes_applied, files_fixed
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go'):
                continue
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if not content: continue
            
            original = content
            
            content = re.sub(r'^\s*\}\),\s*$', lambda m: m.group(0).rstrip().rstrip(','), content, flags=re.MULTILINE)
            content = re.sub(r'^\s*\)\),\s*$', lambda m: m.group(0).rstrip().rstrip(','), content, flags=re.MULTILINE)
            content = re.sub(r'^\s*\]\),\s*$', lambda m: m.group(0).rstrip().rstrip(','), content, flags=re.MULTILINE)
            
            content = re.sub(r'return\s+.*?,\s*$', lambda m: m.group(0).rstrip().rstrip(','), content, flags=re.MULTILINE)
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

fix_all_files()
print(f"SUMMARY: {fixes_applied} fixes across {files_fixed} files")
