#!/usr/bin/env python3
"""
OMNI Phase 10 — Intelligent Brace Repair.

This script analyzes each Go file's brace structure and removes premature closing
braces that cause code to spill outside function bodies.

Key insight: The pattern is usually:
1. A function opens with {
2. An inner block (for/if/switch) opens and closes
3. There's an EXTRA } that closes the function prematurely
4. Remaining code in the function is now outside

Fix: Remove the extra } that prematurely closes the function.
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

def analyze_and_fix_braces(content, fpath=""):
    """
    Walk through the file tracking brace depth. When we hit a } that would 
    take us to depth 0, but there's still indented code below, we know this
    } is premature — remove it.
    """
    lines = content.split('\n')
    
    # First pass: identify all premature closing braces
    removals = set()  # line indices to remove
    
    depth = 0
    func_start = -1
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Track depth
        for ch in stripped:
            if ch == '{':
                if depth == 0:
                    func_start = i
                depth += 1
            elif ch == '}':
                depth -= 1
        
        # If depth just went to 0 (top-level closing brace)
        if depth == 0 and '}' in stripped and stripped == '}':
            # Check if there's still indented code below before the next top-level declaration
            has_orphan_code = False
            next_func_or_type = False
            
            for j in range(i + 1, min(i + 30, len(lines))):
                next_stripped = lines[j].strip()
                if next_stripped == '':
                    continue
                    
                # If next non-empty line is indented code (starts with \t), it's orphaned
                if lines[j].startswith('\t') and not next_stripped.startswith('//'):
                    has_orphan_code = True
                    break
                
                # If next non-empty line is a comment followed by indented code
                if next_stripped.startswith('//'):
                    # Check if the line after the comment is indented
                    for k in range(j + 1, min(j + 5, len(lines))):
                        kstripped = lines[k].strip()
                        if kstripped == '':
                            continue
                        if lines[k].startswith('\t'):
                            has_orphan_code = True
                        break
                    if has_orphan_code:
                        break
                    continue
                    
                # If next is a type/func/package/import/var/const, it's not orphaned
                if (next_stripped.startswith('func ') or 
                    next_stripped.startswith('type ') or
                    next_stripped.startswith('package ') or
                    next_stripped.startswith('import ') or
                    next_stripped.startswith('var ') or
                    next_stripped.startswith('const ')):
                    next_func_or_type = True
                    break
                    
                break
            
            if has_orphan_code and not next_func_or_type:
                # This } is premature — mark for removal
                removals.add(i)
                depth = 1  # We're still inside the function
    
    if not removals:
        return content
    
    # Build new content without the premature braces
    new_lines = []
    for i, line in enumerate(lines):
        if i in removals:
            continue  # Skip premature closing brace
        new_lines.append(line)
    
    return '\n'.join(new_lines)

def fix_orphan_omniresult_struct():
    """Fix files where OmniResult struct is missing closing } and has Error field."""
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
            
            # Pattern: type OmniResult struct {\n\tValue ...\n\tError error\n\n\ntype
            content = re.sub(
                r'type OmniResult struct \{\s*\n\s*Value\s+interface\{\}\s*\n\s*Error\s+error\s*\n\s*\n\s*\ntype',
                'type OmniResult struct {\n\tValue interface{}\n\tErr   error\n}\n\ntype',
                content
            )
            
            # Simpler pattern: missing } between fields and next type/func
            content = re.sub(
                r'type OmniResult struct \{\s*\n\s*Value\s+interface\{\}\s*\n\s*Error\s+error\s*\n\s*\n(type|func)',
                r'type OmniResult struct {\n\tValue interface{}\n\tErr   error\n}\n\n\1',
                content
            )
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_premature_braces():
    """Fix premature closing braces in all Go files."""
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
            
            # Run up to 3 iterations since removing one brace may reveal another
            for _ in range(3):
                new_content = analyze_and_fix_braces(content, fpath)
                if new_content == content:
                    break
                content = new_content
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def main():
    print("=" * 70)
    print("OMNI PHASE 10 — Intelligent Brace Repair")
    print("=" * 70)
    
    print("\n[1] Fixing orphan OmniResult structs...")
    fix_orphan_omniresult_struct()
    
    print("[2] Fixing premature closing braces...")
    fix_premature_braces()
    
    print(f"\nSUMMARY: {fixes_applied} fixes across {files_fixed} files")
    print("=" * 70)

if __name__ == "__main__":
    main()
