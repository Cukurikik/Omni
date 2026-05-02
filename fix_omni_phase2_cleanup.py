#!/usr/bin/env python3
"""
OMNI Phase 2 Cleanup — Remove spurious trailing commas from return/panic statements
and fix remaining issues.
"""

import os
import re

OMNI_ROOT = r"c:\Users\IKYY\Downloads\Omni\src"
fixes_applied = 0
files_fixed = 0

def log_fix(filepath, desc):
    global fixes_applied
    fixes_applied += 1
    rel = os.path.relpath(filepath, OMNI_ROOT)
    print(f"  [FIX] {rel}: {desc}")

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

def fix_spurious_commas():
    """Remove trailing commas from return/panic/statements."""
    global files_fixed
    
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go'):
                continue
            
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if content is None:
                continue
            
            original = content
            
            # Fix: return SomeStruct{...},  -> return SomeStruct{...}
            # Pattern: return ...\},\n
            content = re.sub(r'(\breturn\s+.+\}),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: return ...(...),$  -> return ...(...)
            content = re.sub(r'(\breturn\s+.+\)),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: panic("..."),  -> panic("...")
            content = re.sub(r'(\bpanic\(.+\)),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: return someVar,  -> return someVar  (simple returns)
            content = re.sub(r'(\breturn\s+\w+),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: return nil, -> return nil
            content = re.sub(r'(\breturn\s+nil),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: return true/false, -> return true/false
            content = re.sub(r'(\breturn\s+(?:true|false)),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: return "", -> return ""
            content = re.sub(r'(\breturn\s+"[^"]*"),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: return 0, -> return 0 (but NOT return a, b which is valid multi-return)
            content = re.sub(r'(\breturn\s+\d+(?:\.\d+)?),\s*$', r'\1', content, flags=re.MULTILINE)
            
            if content != original:
                if write_file(fpath, content):
                    log_fix(fpath, "Removed spurious trailing commas from statements")
                    files_fixed += 1

def main():
    print("=" * 70)
    print("OMNI PHASE 2 CLEANUP — Removing Spurious Commas")
    print("=" * 70)
    
    fix_spurious_commas()
    
    print(f"\nSUMMARY: {fixes_applied} fixes across {files_fixed} files")
    print("=" * 70)

if __name__ == "__main__":
    main()
