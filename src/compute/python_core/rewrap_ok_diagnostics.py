"""
Re-wrap diagnostics() returns in Ok() for engines that declare -> Result.
Only wraps single-line `return {...}` patterns.
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
    
    # Only process engines where diagnostics declares -> Result
    if not re.search(r'def diagnostics\(self\)\s*->\s*Result', content):
        continue
    
    original = content
    lines = content.split('\n')
    new_lines = []
    in_diagnostics = False
    diag_indent = 0
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Detect diagnostics method
        if re.match(r'\s+def diagnostics\(self\)\s*->\s*Result', line):
            in_diagnostics = True
            diag_indent = len(line) - len(line.lstrip())
        elif in_diagnostics:
            curr_indent = len(line) - len(line.lstrip()) if stripped else diag_indent + 4
            if stripped and curr_indent <= diag_indent and 'def diagnostics' not in stripped:
                in_diagnostics = False
        
        if in_diagnostics:
            # Wrap `return {...}` with Ok()
            match = re.match(r'(\s+)return\s+(\{.*\})\s*$', line)
            if match:
                indent = match.group(1)
                dict_content = match.group(2)
                # Don't double-wrap
                if 'Ok(' not in line:
                    line = f'{indent}return Ok({dict_content})'
        
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    if content != original:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        fixed += 1

print(f"Re-wrapped {fixed} engines with Ok() in diagnostics")
