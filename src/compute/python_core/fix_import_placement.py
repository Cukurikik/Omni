import os, glob

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'
CANONICAL_IMPORT = 'from src.compute.python_core.omni_base_engine import Result, Ok, Err'
files = glob.glob(os.path.join(TARGET_DIR, 'omni_*_engine.py'))

fixed = 0
for f in files:
    bn = os.path.basename(f)
    if bn == 'omni_base_engine.py':
        continue

    with open(f, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()

    # Step 1: Remove ALL occurrences of the canonical import line
    new_lines = []
    had_import = False
    for line in lines:
        if CANONICAL_IMPORT in line.strip():
            had_import = True
            continue
        new_lines.append(line)

    if not had_import:
        continue

    # Step 2: Find the correct module-level insertion point
    insert_idx = 0
    in_docstring = False
    docstring_char = None

    for i, line in enumerate(new_lines):
        stripped = line.strip()

        # Handle module-level docstrings
        if i == 0 and (stripped.startswith('"""') or stripped.startswith("'''")):
            docstring_char = stripped[:3]
            if stripped.count(docstring_char) >= 2:
                insert_idx = i + 1
            else:
                in_docstring = True
            continue

        if in_docstring:
            if docstring_char and docstring_char in stripped:
                in_docstring = False
                insert_idx = i + 1
            continue

        # Module-level code (not indented)
        first_char = line[0:1] if line else ''
        if first_char not in (' ', '\t', '\r', '\n', ''):
            if stripped.startswith('from ') or stripped.startswith('import '):
                insert_idx = i + 1
            elif stripped.startswith('class ') or stripped.startswith('def ') or stripped.startswith('@'):
                break

    # Insert the import at the correct module-level position
    new_lines.insert(insert_idx, CANONICAL_IMPORT + '\n')

    with open(f, 'w', encoding='utf-8') as fh:
        fh.writelines(new_lines)
    fixed += 1

print(f'Repositioned {fixed} imports to module level')
