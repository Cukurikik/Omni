#!/usr/bin/env python3
"""
OMNI Phase 5 — Fix remaining issues:
1. Spurious commas after goroutine invocations }(args),
2. References to undefined 'result' package 
3. Inconsistent Error vs Err field names
4. OmniResult struct field Error -> Err
5. Various lingering comma issues
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

def fix_goroutine_commas():
    """Remove trailing commas after goroutine invocations: }(args),"""
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
            
            # Fix: }(args),  -> }(args)
            content = re.sub(r'(\}\([^)]*\))\s*,\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: }(),  -> }()
            content = re.sub(r'(\}\(\))\s*,\s*$', r'\1', content, flags=re.MULTILINE)
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_result_package_refs():
    """Replace result.OmniResult[T] with just OmniResult[T] since result is not imported."""
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
            
            # Only fix if result is not actually imported
            if 'result.OmniResult' in content or 'result.Ok' in content or 'result.Err' in content:
                has_import = '"github.com/' in content and 'result"' in content
                if not has_import:
                    content = content.replace('result.OmniResult', 'OmniResult')
                    content = content.replace('result.Ok', 'Ok')
                    content = content.replace('result.Err', 'Err')
                    content = content.replace('result.Fail', 'Fail')
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_error_field_to_err():
    """Change Error field to Err in OmniResult struct definitions."""
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
            
            # Fix OmniResult struct definitions that use Error instead of Err
            # Pattern: type OmniResult struct {\n\tValue ...\n\tError error\n}
            content = re.sub(
                r'(type\s+OmniResult\s+struct\s*\{[^}]*?)\tError\s+error',
                r'\1\tErr   error',
                content
            )
            
            # Fix struct literal Error: field usage for OmniResult
            # Only in files that define OmniResult with Err field
            if 'Err   error' in content:
                # Fix OmniResult{...Error: xxx} -> OmniResult{...Err: xxx}
                content = re.sub(r'OmniResult\{Value:\s*nil,\s*Error:', 'OmniResult{Value: nil, Err:', content)
                content = re.sub(r'OmniResult\{Error:', 'OmniResult{Err:', content)
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_remaining_semicolon_comma_errors():
    """Fix lines that still have commas where semicolons are expected."""
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
                
                # Fix: statement-like lines ending with comma that shouldn't
                # Skip struct/map literal values, function args, array elements
                if stripped.endswith(','):
                    # Is this inside a struct/map literal? Check context
                    # Simple heuristic: if line doesn't have a : for field assignment
                    # and is not inside a composite literal
                    
                    # Check for goroutine/closure invocations
                    if re.match(r'^\s*\}.*\(.*\)\s*,$', line):
                        line = line.rstrip().rstrip(',')
                    
                    # Check for standalone function calls with trailing comma
                    # e.g., fmt.Printf(...),
                    elif re.match(r'^\s*\w+\.\w+\(.*\)\s*,$', line):
                        line = line.rstrip().rstrip(',')
                    
                    # Check for select/switch case statements
                    elif re.match(r'^\s*(case|default)\s*.*:\s*,$', line):
                        line = line.rstrip().rstrip(',')
                
                new_lines.append(line)
            
            content = '\n'.join(new_lines)
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_missing_struct_closing_brace():
    """Find OmniResult structs missing closing brace and fix them."""
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
            
            # Pattern: type OmniResult... struct {\n\tValue ...\n\tErr ...\n\nfunc
            # Missing closing } before func
            content = re.sub(
                r'(type\s+OmniResult\S*\s+struct\s*\{\s*\n\s*Value\s+\S+\s*\n\s*Err\s+error)\s*\n\n(func\s)',
                r'\1\n}\n\n\2',
                content
            )
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def main():
    print("=" * 70)
    print("OMNI PHASE 5 — Remaining Fixes")
    print("=" * 70)
    
    print("\n[1] Fixing goroutine invocation commas...")
    fix_goroutine_commas()
    
    print("[2] Fixing undefined result package references...")
    fix_result_package_refs()
    
    print("[3] Fixing Error->Err field names...")
    fix_error_field_to_err()
    
    print("[4] Fixing remaining semicolon/comma errors...")
    fix_remaining_semicolon_comma_errors()
    
    print("[5] Fixing missing struct closing braces...")
    fix_missing_struct_closing_brace()
    
    print(f"\nSUMMARY: {fixes_applied} fixes across {files_fixed} files")
    print("=" * 70)

if __name__ == "__main__":
    main()
