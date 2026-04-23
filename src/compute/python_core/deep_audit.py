import os
import glob
import ast
import re
import json

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'
TESTS_DIR = r'c:\Users\IKYY\Downloads\Omni\tests\integration'

# Get all engine files
files = glob.glob(os.path.join(TARGET_DIR, 'omni_*_engine.py'))

results = {
    'total_engines': len(files),
    'no_docstring': [],
    'no_diagnostics': [],
    'bespoke_result_class': [],
    'no_base_import': [],
    'syntax_errors': [],
    'isinstance_ok_err': [],
    'try_except_found': [],
}

for f in files:
    basename = os.path.basename(f)
    
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Check syntax
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        results['syntax_errors'].append(basename)
        continue
    
    # Check for bespoke Result/Ok/Err class definitions
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name in ('Result', 'Ok', 'Err'):
            results['bespoke_result_class'].append(basename)
            break
    
    # Check for canonical import
    if 'from src.compute.python_core.omni_base_engine import' not in content:
        if basename != 'omni_base_engine.py':
            results['no_base_import'].append(basename)
    
    # Check for class docstrings
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            if not (node.body and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, (ast.Str, ast.Constant))):
                results['no_docstring'].append(basename)
                break
    
    # Check for diagnostics method
    has_diagnostics = False
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == 'diagnostics':
                    has_diagnostics = True
                    break
    if not has_diagnostics:
        # Check for module-level diagnostics
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == 'diagnostics':
                has_diagnostics = True
                break
    if not has_diagnostics and basename != 'omni_base_engine.py':
        results['no_diagnostics'].append(basename)
    
    # Check for isinstance(x, Ok) or isinstance(x, Err) in engines
    if re.search(r'isinstance\([^,]+,\s*(Ok|Err)\s*\)', content):
        results['isinstance_ok_err'].append(basename)
    
    # Check for try/except blocks
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            results['try_except_found'].append(basename)
            break

print(json.dumps(results, indent=2))
