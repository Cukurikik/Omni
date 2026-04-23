import os, glob, re, py_compile

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'

# Get list of broken files
files = glob.glob(os.path.join(TARGET_DIR, 'omni_*_engine.py'))
bad_files = []
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError:
        bad_files.append(f)

print(f"Found {len(bad_files)} files with syntax errors. Attempting repair...")

fixed = 0
for f in bad_files:
    bn = os.path.basename(f)
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()

    # The primary issue: return Ok({...multi-line dict...}) where only the first
    # line of the dict got wrapped but the closing }) is wrong.
    # Strategy: Revert any broken Ok() wrapping in diagnostics methods
    # by finding Ok({ ... }) patterns that are malformed.
    
    # Approach: Find all `return Ok({` and check if there's a matching `})`
    # If not, the Ok() was partial - revert it.
    
    lines = content.split('\n')
    new_lines = []
    i = 0
    modified = False
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Detect `return Ok({...` on single line without closing `})`
        if 'return Ok({' in stripped and '})' not in stripped:
            # Check if this is a multi-line dict return
            # Find the matching close: look for `})` in subsequent lines
            found_close = False
            for j in range(i + 1, min(i + 50, len(lines))):
                if '})' in lines[j]:
                    found_close = True
                    break
            
            if not found_close:
                # Broken Ok() wrap - revert to raw dict return
                line = line.replace('return Ok({', 'return {')
                modified = True
        
        # Also fix lines that have `}),` or `})` without matching `Ok(`
        # Sometimes the close bracket was already there as `})`
        
        new_lines.append(line)
        i += 1
    
    if modified:
        content = '\n'.join(new_lines)
    
    # Another pattern: the import was inserted in a weird spot inside a string
    # Check for `from src.compute...` appearing inside indented code that's not
    # at the start of a line
    lines2 = content.split('\n')
    cleaned_lines = []
    for line in lines2:
        stripped = line.strip()
        if stripped == 'from src.compute.python_core.omni_base_engine import Result, Ok, Err':
            if line.startswith('    ') or line.startswith('\t'):
                # This is inside a block - remove it (it's already at module level)
                modified = True
                continue
        cleaned_lines.append(line)
    
    if modified:
        content = '\n'.join(cleaned_lines)
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        
        # Check if it compiles now
        try:
            py_compile.compile(f, doraise=True)
            fixed += 1
        except py_compile.PyCompileError:
            pass

print(f"Fixed {fixed} / {len(bad_files)} files")

# Re-check what's still broken
still_bad = []
for f in bad_files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        still_bad.append((os.path.basename(f), str(e)[:150]))

print(f"Still broken: {len(still_bad)}")
for bn, err in still_bad[:10]:
    print(f"  {bn}: {err}")
