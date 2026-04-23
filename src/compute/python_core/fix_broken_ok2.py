import os, glob, py_compile, re

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'
files = glob.glob(os.path.join(TARGET_DIR, 'omni_*_engine.py'))

bad_files = []
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError:
        bad_files.append(f)

print(f"Processing {len(bad_files)} broken files...")

fixed = 0
for f in bad_files:
    bn = os.path.basename(f)
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    original = content
    
    # Fix 1: Replace `return Ok({` ... `})` with `return {` ... `}`
    # Handle multi-line Ok() wrapping by finding all `return Ok({` and changing to `return {`
    content = content.replace('return Ok({', 'return {')
    
    # Fix closing `})` to `}` — but ONLY where it matches a diagnostics dict return
    # This is tricky. Let's use a different approach:
    # Find lines with just `})` or `})\n` that don't match any Ok(...) or function call
    # Actually, the safest is to find `})` at the end of a diagnostics-like block
    # and replace with `}`
    
    # Remove stray `)` after dict closes that were added by Ok() wrapping
    # Pattern: a line that is just whitespace + `})` or `}),`
    content = re.sub(r'^(\s+)\}\)(\s*)$', r'\1}\2', content, flags=re.MULTILINE)
    
    # Fix 2: Remove import lines that appeared inside strings or indented blocks
    lines = content.split('\n')
    cleaned = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == 'from src.compute.python_core.omni_base_engine import Result, Ok, Err':
            if line.startswith('    ') or line.startswith('\t'):
                continue  # Skip indented import
            # Check if this is inside a multi-line string by counting triple-quotes above
            triple_count = sum(1 for l in lines[:i] if '"""' in l)
            if triple_count % 2 == 1:
                continue  # Inside a docstring
        cleaned.append(line)
    content = '\n'.join(cleaned)
    
    if content != original:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        
        try:
            py_compile.compile(f, doraise=True)
            fixed += 1
        except py_compile.PyCompileError:
            pass

print(f"Fixed {fixed} / {len(bad_files)}")

# Final check
still_bad = []
for f in bad_files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        still_bad.append(os.path.basename(f))

print(f"Still broken: {len(still_bad)}")
for bn in still_bad:
    print(f"  {bn}")
