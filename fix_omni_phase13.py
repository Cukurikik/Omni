#!/usr/bin/env python3
"""
OMNI Phase 13 — Fix the damage from Phase 12 by removing commas from:
1. Lines with := (variable declarations got commas)
2. Struct field declarations (type definitions got commas)
3. Lines with = (assignments got commas)
4. Any line inside a struct type definition that has a comma but shouldn't
"""

import os
import re

OMNI_ROOT = r"c:\Users\IKYY\Downloads\Omni\src"
fixes_applied = 0
files_fixed = 0

def read_file(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except:
        return None

def write_file(path, content):
    try:
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        return True
    except:
        return False

def fix_bad_commas():
    """Remove commas that were incorrectly added."""
    global files_fixed, fixes_applied
    
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go'):
                continue
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if content is None:
                continue
            original = content
            lines = content.split('\n')
            new_lines = []
            
            # Track if we're inside a type struct { ... } block
            in_struct_def = False
            struct_depth = 0
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Track struct type definitions
                if re.match(r'^\s*type\s+\w+\s+struct\s*\{', line):
                    in_struct_def = True
                    struct_depth = 1
                elif in_struct_def:
                    struct_depth += stripped.count('{') - stripped.count('}')
                    if struct_depth <= 0:
                        in_struct_def = False
                
                if stripped.endswith(','):
                    should_remove = False
                    
                    # 1. Variable declaration: x := expr,
                    if ':=' in stripped:
                        should_remove = True
                    
                    # 2. Struct field definition (inside type...struct):
                    # FieldName Type,  (no : for assignment)
                    if in_struct_def and ':' not in stripped:
                        # This is a struct field type declaration, not a value
                        if re.match(r'^\s+\w+\s+\S+', line) and not stripped.startswith('//'):
                            should_remove = True
                    
                    # 3. Assignment: x = expr, (NOT field: value,)
                    if '=' in stripped and ':' not in stripped.split('=')[0]:
                        # Make sure it's not inside a composite literal
                        # Heuristic: if line starts with tab and doesn't have Field:
                        if not re.match(r'^\s+\w+\s*:', line):
                            should_remove = True
                    
                    # 4. return statements
                    if stripped.startswith('return '):
                        should_remove = True
                    
                    # 5. panic/defer/go
                    if stripped.startswith(('panic(', 'defer ', 'go ')):
                        should_remove = True
                    
                    # 6. Channel sends: ch <- value,
                    if '<-' in stripped:
                        should_remove = True
                    
                    # 7. Simple function calls (not struct field values)
                    if re.match(r'^\s*\w[\w.]*\(.*\)\s*,$', line) and ':' not in stripped.split('(')[0]:
                        should_remove = True
                    
                    # 8. if/for/switch etc
                    if re.match(r'^\s*(if|for|switch|select|case|default)\b', line):
                        should_remove = True
                    
                    # 9. Import lines
                    if re.match(r'^\s+"[^"]+"\s*,$', line):
                        should_remove = True
                    
                    # 10. continue/break
                    if stripped in ('continue,', 'break,'):
                        should_remove = True
                    
                    # 11. Goroutine closure: }(args),
                    if re.match(r'^\s*\}.*\(.*\)\s*,$', line):
                        should_remove = True
                    
                    if should_remove:
                        line = line.rstrip().rstrip(',')
                
                new_lines.append(line)
            
            content = '\n'.join(new_lines)
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def main():
    print("=" * 70)
    print("OMNI PHASE 13 — Fix Incorrectly Added Commas")
    print("=" * 70)
    
    fix_bad_commas()
    
    print(f"\nSUMMARY: {fixes_applied} fixes across {files_fixed} files")
    print("=" * 70)

if __name__ == "__main__":
    main()
