#!/usr/bin/env python3
"""
OMNI Phase 8 — Structural Repair:
1. Fix OmniResult structs missing closing brace (the #1 issue)
2. Fix functions missing closing brace
3. Fix broken func calls 
4. Fix all remaining Error method trailing commas
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

def fix_struct_missing_brace():
    """Fix struct definitions missing closing brace before next type/func."""
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
            
            # Pattern 1: struct field list not closed before next type/func
            # type X struct {\n\t...\n\n(type|func)
            # Missing } before the blank line
            
            lines = content.split('\n')
            new_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                
                # Check if we're at a field in a struct that's followed by empty+type/func
                if (i + 2 < len(lines) and 
                    stripped and 
                    not stripped.startswith('//') and
                    not stripped.startswith('func ') and
                    not stripped.startswith('type ') and
                    not stripped.startswith('package ') and
                    not stripped.startswith('import ') and
                    not stripped.startswith('const ') and
                    not stripped.startswith('var ') and
                    stripped != '}' and
                    stripped != '{' and
                    stripped != '},'):
                    
                    next_line = lines[i + 1].strip()
                    next_next = lines[i + 2].strip() if i + 2 < len(lines) else ''
                    
                    # Case: field line -> empty line -> type/func
                    if (next_line == '' and 
                        (next_next.startswith('type ') or next_next.startswith('func '))):
                        
                        # Check if we're inside an unclosed struct
                        # Count braces from the nearest type...struct { above
                        brace_count = 0
                        found_struct = False
                        for j in range(i, -1, -1):
                            l = lines[j]
                            brace_count += l.count('{') - l.count('}')
                            if 'struct {' in l or 'struct{' in l:
                                found_struct = True
                                break
                            if l.strip().startswith('func ') and '{' in l:
                                # We're inside a func, not a struct
                                found_struct = False
                                break
                        
                        if found_struct and brace_count > 0:
                            # Need to close the struct
                            new_lines.append(line)
                            new_lines.append('}')
                            i += 1
                            continue
                    
                    # Case: field line -> type/func (no blank line)
                    if (next_line.startswith('type ') or next_line.startswith('func ')):
                        brace_count = 0
                        found_struct = False
                        for j in range(i, -1, -1):
                            l = lines[j]
                            brace_count += l.count('{') - l.count('}')
                            if 'struct {' in l or 'struct{' in l:
                                found_struct = True
                                break
                            if l.strip().startswith('func ') and '{' in l:
                                found_struct = False
                                break
                        
                        if found_struct and brace_count > 0:
                            new_lines.append(line)
                            new_lines.append('}')
                            i += 1
                            continue
                
                new_lines.append(line)
                i += 1
            
            content = '\n'.join(new_lines)
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_func_missing_brace():
    """Fix functions missing their closing brace (EOF without })."""
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
            
            # Count total braces
            open_count = content.count('{')
            close_count = content.count('}')
            
            if open_count > close_count:
                diff = open_count - close_count
                # Add missing closing braces at the end
                content = content.rstrip() + '\n'
                for _ in range(diff):
                    content += '}\n'
                
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_return_comma():
    """Fix remaining return statement trailing commas."""
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
            
            # Fix Error() string method trailing comma
            content = re.sub(
                r'(\treturn\s+"[^"]*"\s*\+\s*\w[\w.]*),\s*$',
                r'\1',
                content, flags=re.MULTILINE
            )
            
            # Fix any return with Sprintf etc trailing comma
            content = re.sub(
                r'(\treturn\s+fmt\.\w+\(.*\)),\s*$',
                r'\1',
                content, flags=re.MULTILINE
            )
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def main():
    print("=" * 70)
    print("OMNI PHASE 8 — Structural Repair")
    print("=" * 70)
    
    print("\n[1] Fixing struct missing braces...")
    fix_struct_missing_brace()
    
    print("[2] Fixing function missing braces...")
    fix_func_missing_brace()
    
    print("[3] Fixing return statement commas...")
    fix_return_comma()
    
    print(f"\nSUMMARY: {fixes_applied} fixes across {files_fixed} files")
    print("=" * 70)

if __name__ == "__main__":
    main()
