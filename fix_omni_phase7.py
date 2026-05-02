#!/usr/bin/env python3
"""
OMNI Phase 7 — Final cleanup:
1. Fix ALL remaining commas in import blocks (space-indented too)
2. Fix literal \\n at end of files
3. Fix result.NewError -> Err with errors.New
4. Fix Fail[T]() calls that don't exist (should be Err[T])
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

def fix_all_import_commas():
    """Remove commas from import block entries regardless of indentation."""
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
            
            # Fix: any import line with trailing comma
            # "package/path",  -> "package/path"
            content = re.sub(r'(\s+"[^"]+"),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: spaces indented imports
            content = re.sub(r'(    "[^"]+"),\s*$', r'\1', content, flags=re.MULTILINE)
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_backslash_n():
    """Remove literal \\n at end of files."""
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
            
            # Fix literal \n at end
            if content.endswith('\\n\n') or content.endswith('\\n'):
                content = content.rstrip('\\n').rstrip() + '\n'
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_result_newError():
    """Fix result.NewError -> use local error patterns."""
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
            
            # Fix: result.NewError[T](errors.New("...")) -> Err[T](errors.New("..."))
            content = content.replace('result.NewError', 'Err')
            
            # Fix: Fail[T]("msg") -> Err[T](errors.New("msg"))
            content = re.sub(
                r'Fail\[(\w+)\]\("([^"]+)"\)',
                r'Err[\1](errors.New("\2"))',
                content
            )
            
            # Ensure errors import if needed
            if 'errors.New' in content and '"errors"' not in content:
                if 'import (' in content:
                    content = content.replace('import (', 'import (\n\t"errors"', 1)
                else:
                    pkg_match = re.search(r'(package\s+\w+\s*\n)', content)
                    if pkg_match:
                        content = content[:pkg_match.end()] + '\nimport "errors"\n' + content[pkg_match.end():]
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_closing_paren_comma():
    """Fix import blocks ending with ),  instead of )"""
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
            
            # Fix: ),  ->  )  at end of import blocks
            content = re.sub(r'^(\s*\)),\s*$', r'\1', content, flags=re.MULTILINE)
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def main():
    print("=" * 70)
    print("OMNI PHASE 7 — Final Cleanup")
    print("=" * 70)
    
    print("\n[1] Fixing import block commas...")
    fix_all_import_commas()
    
    print("[2] Fixing literal \\n at file end...")
    fix_backslash_n()
    
    print("[3] Fixing result.NewError references...")
    fix_result_newError()
    
    print("[4] Fixing closing paren commas...")
    fix_closing_paren_comma()
    
    print(f"\nSUMMARY: {fixes_applied} fixes across {files_fixed} files")
    print("=" * 70)

if __name__ == "__main__":
    main()
