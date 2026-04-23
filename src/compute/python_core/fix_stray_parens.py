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
    
    # Fix pattern 1: `}),` at end of line in dict context -> `},`
    # This happens when Ok({ was stripped but }) remained
    content = re.sub(r'\}\),(\s*)$', r'},\1', content, flags=re.MULTILINE)
    
    # Fix pattern 2: `})` alone on a line -> `}`
    content = re.sub(r'^(\s+)\}\)(\s*)$', r'\1}\2', content, flags=re.MULTILINE)
    
    # Fix pattern 3: import line stuck inside an indented block
    lines = content.split('\n')
    cleaned = []
    canonical = 'from src.compute.python_core.omni_base_engine import Result, Ok, Err'
    for line in lines:
        stripped = line.strip()
        if stripped == canonical and (line.startswith('    ') or line.startswith('\t')):
            continue
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

still_bad = []
for f in bad_files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        still_bad.append((os.path.basename(f), str(e)[:200]))

print(f"Still broken: {len(still_bad)}")
for bn, err in still_bad[:10]:
    print(f"  {bn}:")
    print(f"    {err}")
