"""
Fix pre-existing stray `)` at end of return dict statements.
Pattern: `return {...})` -> `return {...}` (unmatched paren)
"""
import os
import glob
import py_compile
import re

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'
files = glob.glob(os.path.join(TARGET_DIR, 'omni_*_engine.py'))

# First identify broken files
bad_files = []
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError:
        bad_files.append(f)

print(f"Found {len(bad_files)} files with syntax errors")

fixed = 0
still_broken = []
for f in bad_files:
    bn = os.path.basename(f)
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    original = content
    
    # Fix pattern 1: `return {...})` at end of single-line return  
    # This is a dict return with a stray `)` after the `}`
    content = re.sub(r'return\s+(\{[^{}]*\})\)', r'return \1', content)
    
    # Fix pattern 2: Multi-line return dict ending with `})` 
    # where `})` should be `}` (no matching `Ok(` or function call)
    # We detect this by checking if there's an unmatched `)` at end of a dict
    
    if content != original:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        try:
            py_compile.compile(f, doraise=True)
            fixed += 1
        except py_compile.PyCompileError as e:
            still_broken.append((bn, str(e)[:120]))
    else:
        still_broken.append((bn, "No pattern match"))

print(f"Fixed {fixed} / {len(bad_files)}")
print(f"Still broken: {len(still_broken)}")
for bn, err in still_broken[:10]:
    print(f"  {bn}: {err}")
