"""
Fix indentation errors introduced by the docstring injection script.
Removes the bad docstrings and adds them back with correct 4-space indentation relative to the class declaration.
"""
import os
import glob
import ast
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
    
    # Check if the file has the bad docstring
    if 'OMNI Zero-Prod Production Implementation for' not in content:
        continue
        
    lines = content.split('\n')
    new_lines = []
    
    # Simply remove the bad docstrings
    for line in lines:
        if '"""OMNI Zero-Prod Production Implementation for' in line:
            continue
        new_lines.append(line)
        
    content_clean = '\n'.join(new_lines)
    
    # Re-inject docstrings properly
    try:
        tree = ast.parse(content_clean)
    except SyntaxError as e:
        print(f"Could not parse cleaned file {bn}: {e}")
        continue
        
    lines = content_clean.split('\n')
    insertions = []
    
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            has_doc = (node.body and getattr(node.body[0], "value", None) and isinstance(node.body[0].value, (ast.Str, ast.Constant)))
            if not has_doc:
                # The node.lineno is the `class ` line
                class_line = node.lineno - 1
                base_indent = lines[class_line][:len(lines[class_line]) - len(lines[class_line].lstrip())]
                proper_indent = base_indent + '    '
                
                # Insert right after the class def 
                # (Need to account for decorators, so we insert after the line with the ':' that starts the class body)
                insert_line = class_line + 1
                while insert_line < len(lines) and not lines[insert_line - 1].strip().endswith(':'):
                    insert_line += 1
                
                insertions.append((insert_line, f'{proper_indent}"""OMNI Zero-Prod Production Implementation for {node.name}."""'))
                
    insertions.sort(key=lambda x: x[0], reverse=True)
    for idx, text in insertions:
        lines.insert(idx, text)
        
    with open(f, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines))
        
    fixed += 1

print(f"Fixed {fixed} files with bad docstrings")
