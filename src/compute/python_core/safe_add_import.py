"""
Add canonical import to engines that don't have it, at module level.
Safe approach: only add if engine doesn't already have it.
"""
import os
import glob
import py_compile

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'
CANONICAL = 'from src.compute.python_core.omni_base_engine import Result, Ok, Err'
files = glob.glob(os.path.join(TARGET_DIR, 'omni_*_engine.py'))

added = 0
for f in files:
    bn = os.path.basename(f)
    if bn == 'omni_base_engine.py':
        continue
    
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    # Skip if already has the import
    if CANONICAL in content:
        continue
    
    lines = content.split('\n')
    
    # Find the correct insertion point: after all module-level imports, before class/def
    insert_idx = 0
    in_docstring = False
    docstring_char = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Track module-level docstrings
        if not in_docstring:
            if stripped.startswith('"""') or stripped.startswith("'''"):
                docstring_char = stripped[:3]
                if stripped.count(docstring_char) >= 2:
                    # Single-line docstring
                    insert_idx = max(insert_idx, i + 1)
                else:
                    in_docstring = True
                continue
        
        if in_docstring:
            if docstring_char and docstring_char in stripped:
                in_docstring = False
                insert_idx = max(insert_idx, i + 1)
            continue
        
        # Module-level code (not indented)
        first_char = line[0:1] if line else ''
        if first_char not in (' ', '\t', '\r', '\n', ''):
            if stripped.startswith('from ') or stripped.startswith('import '):
                insert_idx = max(insert_idx, i + 1)
            elif stripped.startswith('class ') or stripped.startswith('def ') or stripped.startswith('@'):
                break
            elif stripped.startswith('#') or stripped.startswith('ENGINE_') or stripped == '':
                insert_idx = max(insert_idx, i + 1)
    
    # Also handle `from __future__` - must insert AFTER it
    for i, line in enumerate(lines):
        if 'from __future__' in line:
            insert_idx = max(insert_idx, i + 1)
    
    lines.insert(insert_idx, CANONICAL)
    new_content = '\n'.join(lines)
    
    # Verify it compiles before writing
    try:
        compile(new_content, f, 'exec')
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(new_content)
        added += 1
    except SyntaxError:
        # Don't write if it breaks compilation
        pass

print(f"Added canonical import to {added} engines")

# Verify
err_count = 0
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError:
        err_count += 1
print(f"Post-add compile errors: {err_count} / {len(files)}")
