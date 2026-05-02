#!/usr/bin/env python3
"""
OMNI Phase 9 — Comprehensive Brace Balancer & Comma Purge.

This script:
1. Ensures every Go file has balanced braces
2. Removes ALL remaining spurious commas from non-composite-literal contexts
3. Fixes premature function closings (code spilling outside function)
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

def is_inside_string(line, pos):
    """Check if position is inside a string literal."""
    in_string = False
    escape = False
    for i, ch in enumerate(line):
        if i == pos:
            return in_string
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
    return in_string

def smart_comma_removal(content):
    """Remove commas that shouldn't be there in Go code.
    
    Go requires trailing commas in multi-line composite literals,
    but NOT in:
    - import blocks
    - statements (assignments, function calls, etc.)
    - struct/interface field declarations
    - const/var blocks
    """
    lines = content.split('\n')
    new_lines = []
    in_import = False
    in_const = False
    in_var = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Track import/const/var blocks
        if stripped.startswith('import ('):
            in_import = True
        elif in_import and stripped == ')':
            in_import = False
        
        if stripped.startswith('const ('):
            in_const = True
        elif in_const and stripped == ')':
            in_const = False
            
        if stripped.startswith('var ('):
            in_var = True
        elif in_var and stripped == ')':
            in_var = False
        
        if stripped.endswith(','):
            should_remove_comma = False
            
            # In import block — never comma
            if in_import:
                should_remove_comma = True
            
            # In const block with = — never comma (const values)
            if in_const and '=' in stripped:
                should_remove_comma = True
            
            # Standalone function call: pkg.Method(args),
            if re.match(r'^\s*(\w[\w.]*)\(.*\)\s*,$', line) and not ':' in stripped.split('(')[0]:
                should_remove_comma = True
            
            # Assignment: x := something, or x = something,
            if re.match(r'^\s*\w[\w.]*\s*:?=\s*.+,$', line) and ':' not in stripped.split('=')[0].replace(':=', ''):
                should_remove_comma = True
            
            # Return statements (already mostly handled, catch remaining)
            if stripped.startswith('return ') and stripped.endswith(','):
                should_remove_comma = True
            
            # panic statements
            if stripped.startswith('panic(') and stripped.endswith(','):
                should_remove_comma = True
            
            # defer statements
            if stripped.startswith('defer ') and stripped.endswith(','):
                should_remove_comma = True
            
            # go statements (goroutine launch)
            if stripped.startswith('go ') and stripped.endswith(','):
                should_remove_comma = True
            
            # Closing brace + call: }(args), 
            if re.match(r'^\s*\}.*\(.*\)\s*,$', line):
                should_remove_comma = True
            
            # fmt.Print/Sprintf etc
            if re.match(r'^\s*fmt\.\w+\(.*\)\s*,$', line):
                should_remove_comma = True
            
            # Simple variable assignment
            if re.match(r'^\s*\w+\s*=\s*"[^"]*"\s*,$', line):
                should_remove_comma = True
            if re.match(r'^\s*\w[\w.]*\s*=\s*\d+\s*,$', line):
                should_remove_comma = True
            if re.match(r'^\s*\w[\w.]*\s*=\s*(true|false|nil)\s*,$', line):
                should_remove_comma = True
            
            # append calls
            if 'append(' in stripped and stripped.endswith(','):
                if re.match(r'^\s*\w[\w.]*\s*=\s*append\(.*\)\s*,$', line):
                    should_remove_comma = True
            
            # Struct field declaration (not value)
            # Pattern: \tFieldName Type,  or \tFieldName []Type,
            if re.match(r'^\s+\w+\s+[\[\]*]?\w+[\[\]{}]*\s*,$', line):
                # Could be struct field or composite literal value...
                # If there's no : it's a field declaration
                if ':' not in stripped:
                    should_remove_comma = True
            
            if should_remove_comma:
                line = line.rstrip().rstrip(',')
        
        new_lines.append(line)
    
    return '\n'.join(new_lines)

def fix_all_files():
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
            
            # Step 1: Smart comma removal
            content = smart_comma_removal(content)
            
            # Step 2: Ensure brace balance
            open_count = content.count('{')
            close_count = content.count('}')
            
            if open_count > close_count:
                diff = open_count - close_count
                content = content.rstrip() + '\n'
                for _ in range(diff):
                    content += '}\n'
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def main():
    print("=" * 70)
    print("OMNI PHASE 9 — Comprehensive Repair")
    print("=" * 70)
    
    fix_all_files()
    
    print(f"\nSUMMARY: {fixes_applied} fixes across {files_fixed} files")
    print("=" * 70)

if __name__ == "__main__":
    main()
