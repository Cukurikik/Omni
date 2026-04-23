import os
import glob
import ast

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'

def remove_classes_ast(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False

    classes_to_remove = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name in ('Result', 'Ok', 'Err'):
            classes_to_remove.append(node)
            
    if not classes_to_remove:
        return False

    # Extract lines to remove based on AST nodes
    lines = source.split('\n')
    lines_to_keep = []
    
    # Track sets of line numbers to skip
    skip_lines = set()
    for node in classes_to_remove:
        start = node.lineno - 1
        
        # If there are decorators, start from the first one
        if node.decorator_list:
            start = node.decorator_list[0].lineno - 1
            
        end = node.end_lineno
        for i in range(start, end):
            skip_lines.add(i)

    for i, line in enumerate(lines):
        if i not in skip_lines:
            lines_to_keep.append(line)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines_to_keep))
        
    return True

files = glob.glob(os.path.join(TARGET_DIR, 'omni_*_engine.py'))
count = 0
for f in files:
    if remove_classes_ast(f):
        count += 1

print(f"Removed bespoke classes from {count} files via AST.")
