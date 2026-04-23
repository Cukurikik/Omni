"""
Revert Ok() wrapping on diagnostics() return values.
The OMNI convention is that diagnostics() returns a raw dict, not a Result.
"""
import os
import glob
import re

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'
files = glob.glob(os.path.join(TARGET_DIR, 'omni_*_engine.py'))

fixed = 0
for f in files:
    bn = os.path.basename(f)
    if bn == 'omni_base_engine.py':
        continue
    
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    original = content
    
    # Find diagnostics methods and revert Ok() wrapping on single-line returns
    # Pattern: `return Ok({...})`  inside diagnostics -> `return {...}`
    # Single line
    content = re.sub(
        r'(def diagnostics\([^)]*\)[^:]*:.*?)(return\s+Ok\()(\{)',
        lambda m: m.group(1) + 'return ' + m.group(3),
        content,
        flags=re.DOTALL
    )
    
    # That's too greedy. Let me use line-by-line approach instead.
    content = original  # reset
    
    lines = content.split('\n')
    in_diagnostics = False
    diag_indent = 0
    new_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if 'def diagnostics(' in stripped:
            in_diagnostics = True
            diag_indent = len(line) - len(line.lstrip())
        
        if in_diagnostics:
            curr_indent = len(line) - len(line.lstrip()) if stripped else diag_indent + 4
            if stripped and curr_indent <= diag_indent and i > 0 and 'def diagnostics(' not in stripped:
                in_diagnostics = False
            else:
                # Inside diagnostics - revert Ok() wrapping
                if 'return Ok(' in stripped:
                    line = line.replace('return Ok(', 'return ')
                    # If the line ends with `})`, change to `}`
                    # But only the LAST `)` that closes Ok()
                    # This is at the end of a multi-line dict
                
                # Check for closing `})` that belongs to Ok() at end of diagnostics return
                # If we see just `})` and we're in a diagnostics return block
                if stripped == '})':
                    line = line.replace('})', '}')
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    if content != original:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        fixed += 1

print(f"Reverted Ok() wrapping in {fixed} engines")
