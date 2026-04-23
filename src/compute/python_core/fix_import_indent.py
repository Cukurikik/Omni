import os, glob, re

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'
CANONICAL_IMPORT = 'from src.compute.python_core.omni_base_engine import Result, Ok, Err'
files = glob.glob(os.path.join(TARGET_DIR, 'omni_*_engine.py'))

fixed = 0
for f in files:
    bn = os.path.basename(f)
    if bn == 'omni_base_engine.py':
        continue

    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    if CANONICAL_IMPORT not in content:
        continue
    
    lines = content.split('\n')
    
    # Check if the import is indented (inside a class/function)
    bad = False
    for i, line in enumerate(lines):
        if CANONICAL_IMPORT in line:
            if line.startswith(' ') or line.startswith('\t'):
                bad = True
                # Remove it from current position
                lines.pop(i)
                break
    
    if bad:
        # Re-insert at module level: find last module-level import or after module docstring
        insert_idx = 0
        in_docstring = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Track module-level docstrings
            if i == 0 and stripped.startswith('\"\"\"'):
                if stripped.count('\"\"\"') >= 2:
                    insert_idx = i + 1
                else:
                    in_docstring = True
                continue
            
            if in_docstring:
                if '\"\"\"' in stripped:
                    in_docstring = False
                    insert_idx = i + 1
                continue
            
            # Module-level imports (not indented)
            if not line.startswith(' ') and not line.startswith('\t'):
                if stripped.startswith('from ') or stripped.startswith('import '):
                    insert_idx = i + 1
                elif stripped.startswith('class ') or stripped.startswith('def '):
                    break  # Stop before class/function definitions
        
        lines.insert(insert_idx, CANONICAL_IMPORT)
        content = '\n'.join(lines)
        
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        fixed += 1

print(f'Repositioned {fixed} imports to module level')
