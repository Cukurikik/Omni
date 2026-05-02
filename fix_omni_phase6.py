#!/usr/bin/env python3
"""
OMNI Phase 6 — Targeted remaining fixes:
1. Assignment statement trailing commas: x = value,
2. append() trailing commas
3. Missing function closing braces (heuristic)
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

def fix_all_trailing_commas():
    """Comprehensive fix for all remaining spurious trailing commas in Go code."""
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
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                if stripped.endswith(','):
                    # Context: is this inside a composite literal (struct, map, array, func args)?
                    # If not, remove the comma
                    
                    # Lines that should NEVER end with comma:
                    # 1. Simple assignments: x = value,  or x := value,
                    # 2. append(): x = append(x, y),
                    # 3. Function calls as statements: foo.Bar(),
                    # 4. String assignments: x = "string",
                    # 5. Boolean/numeric assignments
                    # 6. Variable declarations with := or =
                    
                    should_remove = False
                    
                    # Assignment with := or = (but NOT struct field like Field: value,)
                    if re.match(r'^\s*\w[\w.]*\s*:?=\s*.+,$', line) and ':' not in stripped.split('=')[0]:
                        should_remove = True
                    
                    # append(...),
                    if re.search(r'append\([^)]+\)\s*,$', stripped):
                        should_remove = True
                    
                    # Standalone function call: pkg.Func(...),  or Func(...),
                    if re.match(r'^\s*\w[\w.]*\([^)]*\)\s*,$', line):
                        should_remove = True
                    
                    # n.votedFor = "", style
                    if re.match(r'^\s*\w[\w.]*\s*=\s*"[^"]*"\s*,$', line):
                        should_remove = True
                    
                    # Variable = number,
                    if re.match(r'^\s*\w[\w.]*\s*=\s*\d+\s*,$', line):
                        should_remove = True
                    
                    # Variable = bool,
                    if re.match(r'^\s*\w[\w.]*\s*=\s*(true|false)\s*,$', line):
                        should_remove = True
                    
                    # time.Sleep(...), or similar
                    if re.match(r'^\s*\w+\.\w+\(.*\)\s*,$', line):
                        should_remove = True
                    
                    if should_remove:
                        line = line.rstrip().rstrip(',')
                
                new_lines.append(line)
            
            content = '\n'.join(new_lines)
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_missing_function_braces():
    """Add missing closing braces for functions."""
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
            
            # Pattern: return &Struct{...}\n// Comment or func (missing })
            # The function's return closes the struct but not the function
            content = re.sub(
                r'(\treturn\s+&\w+\{[^}]*\})\s*\n(// )',
                r'\1\n}\n\n\2',
                content
            )
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def main():
    print("=" * 70)
    print("OMNI PHASE 6 — Final Comma & Brace Fixes")
    print("=" * 70)
    
    print("\n[1] Fixing all remaining trailing commas...")
    fix_all_trailing_commas()
    
    print("[2] Fixing missing function braces...")
    fix_missing_function_braces()
    
    print(f"\nSUMMARY: {fixes_applied} fixes across {files_fixed} files")
    print("=" * 70)

if __name__ == "__main__":
    main()
