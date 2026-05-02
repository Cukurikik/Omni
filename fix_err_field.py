"""
OMNI Production Fix: Standardize OmniResult struct field from Err -> Error
across the entire src/ codebase.

This fixes the systemic issue where OmniResult has field 'Error error'
but code uses 'Err:' in struct literals and '.Err' in field access.
"""
import os
import re

SRC_ROOT = r"c:\Users\IKYY\Downloads\Omni\src"

fixed_files = 0
total_replacements = 0

for root, dirs, files in os.walk(SRC_ROOT):
    for fname in files:
        if not fname.endswith('.go'):
            continue
        fpath = os.path.join(root, fname)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception:
            continue
        
        original = content
        
        # Fix 1: Struct literal field "Err:" -> "Error:" in OmniResult-like structs
        # Pattern: { ... Err: errors.New(...) } or { ... Err: fmt.Errorf(...) } etc.
        content = re.sub(
            r'(\{[^}]*?)\bErr:(\s*(?:errors\.New|fmt\.Errorf|err\b|nil))',
            r'\1Error:\2',
            content
        )
        
        # Fix 2: Direct field access ".Err " -> ".Error " (when followed by space, != etc.)
        # But be careful not to match ".Error" -> ".Erroror"
        content = re.sub(
            r'\.Err\b(?!or)',
            '.Error',
            content
        )
        
        # Fix 3: Struct literal field "Err:" standalone at end of struct literal
        content = re.sub(
            r'\bErr:(\s)',
            r'Error:\1',
            content
        )
        
        if content != original:
            try:
                with open(fpath, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files += 1
                count = sum(1 for a, b in zip(original, content) if a != b)
                total_replacements += content.count('Error:') - original.count('Error:')
            except Exception as e:
                print(f"  ERROR writing {fpath}: {e}")

print(f"\n=== OMNI Err->Error Field Fix Complete ===")
print(f"Files modified: {fixed_files}")
print(f"Approximate field replacements: {total_replacements}")
