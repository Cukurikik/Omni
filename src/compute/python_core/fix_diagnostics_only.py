import os, glob, py_compile, re, ast

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'
files = glob.glob(os.path.join(TARGET_DIR, 'omni_*_engine.py'))

# Get just the broken ones
bad_files = []
for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError:
        bad_files.append(f)

print(f"Processing {len(bad_files)} broken files...")

# For these files, we need to REVERT all the `})` -> `}` changes we made,
# and then ONLY apply them inside diagnostics() methods.

fixed = 0
for f in bad_files:
    bn = os.path.basename(f)
    with open(f, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()

    # Step 1: Revert `},` back to `}),` and `}` back to `})` where they were changed
    # Actually, the safer approach: just revert ALL changes by undoing the `}),` -> `},` and `})` -> `}` 
    # But we don't know which were original and which were changed.
    
    # Better approach: Re-read the problematic file and find the diagnostics() method,
    # then only fix stray `)` within that method's return dict.
    
    content = ''.join(lines)
    
    # Find diagnostics method boundaries using line-by-line analysis
    new_lines = []
    in_diagnostics = False
    diag_indent = 0
    return_depth = 0
    i = 0
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # Detect start of diagnostics method
        if 'def diagnostics(' in stripped and not in_diagnostics:
            in_diagnostics = True
            diag_indent = len(line) - len(line.lstrip())
            new_lines.append(line)
            i += 1
            continue
        
        # If we're in diagnostics, check if we've exited
        if in_diagnostics:
            curr_indent = len(line) - len(line.lstrip()) if stripped else diag_indent + 4
            if stripped and curr_indent <= diag_indent and not stripped.startswith('#') and not stripped.startswith('"""'):
                in_diagnostics = False
                # Fall through to normal processing
            else:
                # Inside diagnostics - fix stray `)` in dict returns
                # Pattern: `}),` should be `},` ONLY if not part of a function call
                # Since we're inside diagnostics return dict, `}),` is almost certainly wrong
                if stripped == '}),':
                    line = line.replace('}),', '},')
                elif stripped == '})':
                    line = line.replace('})', '}')
                new_lines.append(line)
                i += 1
                continue
        
        new_lines.append(line)
        i += 1
    
    new_content = ''.join(new_lines)
    
    # Also fix: import line stuck in wrong position
    # Remove any import that's indented
    final_lines = []
    canonical = 'from src.compute.python_core.omni_base_engine import Result, Ok, Err'
    for line in new_content.split('\n'):
        stripped = line.strip()
        if stripped == canonical and (line.startswith('    ') or line.startswith('\t')):
            continue
        final_lines.append(line)
    new_content = '\n'.join(final_lines)
    
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write(new_content)
    
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
for bn, err in still_bad[:15]:
    print(f"  {bn}: {err[:100]}")
