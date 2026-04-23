"""
Fix tests that try to subscript a Result object from diagnostics().
Replaces `diag = engine.diagnostics()` with unwrap logic.
"""
import os
import glob
import re

TESTS_DIR = r'c:\Users\IKYY\Downloads\Omni\tests\integration'
test_files = glob.glob(os.path.join(TESTS_DIR, 'test_semester10_batch*.py'))

fixed_count = 0
for f in test_files:
    with open(f, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    original = content
    
    # Pattern: `diag = engine.diagnostics()` followed by `diag["key"]` usage
    # Replace with: `_raw = engine.diagnostics(); diag = _raw.unwrap() if hasattr(_raw, 'unwrap') else _raw`
    # But we need to be careful not to break things that already work.
    
    # Strategy: Add a helper at the top of each test file that needs it
    helper = '''
def _unwrap_diag(result):
    """Unwrap Result to dict if needed."""
    if hasattr(result, 'unwrap'):
        return result.unwrap()
    return result
'''
    
    # Find all patterns where diagnostics() result is subscripted
    # e.g.,  diag = engine.diagnostics() ... diag["key"]
    # or     result = engine.diagnostics() ... result["key"]
    
    lines = content.split('\n')
    needs_fix = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Look for `var = something.diagnostics()` or `var = ClassName.diagnostics()`
        match = re.match(r'(\s+)(\w+)\s*=\s*\w+\.diagnostics\(\)', stripped)
        if match:
            var_name = match.group(2)
            # Check if this variable is later used with subscript
            for j in range(i+1, min(i+20, len(lines))):
                if f'{var_name}["' in lines[j] or f"{var_name}['" in lines[j]:
                    needs_fix = True
                    break
    
    if needs_fix:
        # Add helper if not already present
        if '_unwrap_diag' not in content:
            # Insert helper after imports
            import_end = 0
            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('import ') or stripped.startswith('from '):
                    import_end = i + 1
            lines.insert(import_end, helper)
        
        content = '\n'.join(lines)
        
        # Now wrap all `var = x.diagnostics()` with _unwrap_diag
        content = re.sub(
            r'(\s+)(\w+)\s*=\s*(\w+\.diagnostics\(\))',
            r'\1\2 = _unwrap_diag(\3)',
            content
        )
        
        # Don't double-wrap
        content = content.replace('_unwrap_diag(_unwrap_diag(', '_unwrap_diag(')
        content = content.replace('))', ')') if '_unwrap_diag(_unwrap_diag' in content else content
    
    if content != original:
        with open(f, 'w', encoding='utf-8') as fh:
            fh.write(content)
        fixed_count += 1

print(f"Fixed {fixed_count} test files")
