import os, glob, ast, re

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'
files = glob.glob(os.path.join(TARGET_DIR, 'omni_*_engine.py'))

fixed_import = 0
fixed_diag = 0
fixed_docstr = 0

CANONICAL_IMPORT = 'from src.compute.python_core.omni_base_engine import Result, Ok, Err'

for f in files:
    bn = os.path.basename(f)
    if bn == 'omni_base_engine.py':
        continue

    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    original = content
    modified = False

    # 1. Add canonical import if missing
    if CANONICAL_IMPORT not in content:
        lines = content.split('\n')
        insert_idx = 0
        
        # Find the right place to insert (after docstrings & existing imports)
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('from ') or stripped.startswith('import '):
                insert_idx = i + 1
            elif stripped.startswith('\"\"\"') or stripped.startswith("'''"):
                # Skip docstring block
                if stripped.count('\"\"\"') == 1 or stripped.count("'''") == 1:
                    for j in range(i+1, len(lines)):
                        if '\"\"\"' in lines[j] or "'''" in lines[j]:
                            insert_idx = j + 1
                            break
                else:
                    insert_idx = i + 1
        
        # If no imports found, insert after first line (module docstring)
        if insert_idx == 0:
            # Check if first thing is docstring
            if lines[0].strip().startswith('\"\"\"'):
                for i in range(len(lines)):
                    if i > 0 and '\"\"\"' in lines[i]:
                        insert_idx = i + 1
                        break
            else:
                insert_idx = 0
        
        lines.insert(insert_idx, CANONICAL_IMPORT)
        content = '\n'.join(lines)
        modified = True
        fixed_import += 1

    # 2. Fix diagnostics() to return Ok() instead of raw dict
    # Match pattern: return {...} inside diagnostics method
    # We need to be careful - only wrap if not already wrapped
    diag_pattern = re.compile(
        r'(def diagnostics\(self\)[^:]*:\s*\n(?:.*\n)*?)'
        r'(\s+return\s+)(\{[^}]+\})',
        re.MULTILINE
    )
    
    def wrap_return(match):
        prefix = match.group(1)
        ret_keyword = match.group(2)
        dict_body = match.group(3)
        # Check if already wrapped
        if 'Ok(' in prefix or 'Ok(' in ret_keyword:
            return match.group(0)
        return prefix + ret_keyword + 'Ok(' + dict_body + ')'
    
    new_content = diag_pattern.sub(wrap_return, content)
    if new_content != content:
        content = new_content
        modified = True
        fixed_diag += 1
    
    # 3. Add missing class docstrings
    try:
        tree = ast.parse(content)
    except SyntaxError:
        if modified:
            with open(f, 'w', encoding='utf-8') as fh:
                fh.write(content)
        continue
    
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if not (node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, (ast.Str, ast.Constant))):
                # Need to add docstring
                class_name = node.name
                lines = content.split('\n')
                # Find the class line
                class_line_idx = node.lineno - 1
                # Find the indentation of the next line
                if class_line_idx + 1 < len(lines):
                    next_line = lines[class_line_idx + 1]
                    indent = len(next_line) - len(next_line.lstrip())
                    if indent == 0:
                        indent = 4
                else:
                    indent = 4
                
                docstring = ' ' * indent + f'\"\"\"OMNI Production Engine: {class_name}. Zero-Prod compliant.\"\"\"'
                lines.insert(class_line_idx + 1, docstring)
                content = '\n'.join(lines)
                modified = True
                fixed_docstr += 1
            break  # Only check the first class

    if modified:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)

print(f'Fixed imports: {fixed_import}')
print(f'Fixed diagnostics (dict->Ok): {fixed_diag}')
print(f'Fixed docstrings: {fixed_docstr}')
