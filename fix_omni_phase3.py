#!/usr/bin/env python3
"""
OMNI Phase 3 — Fix import block commas, remaining specific file issues.
"""

import os
import re

OMNI_ROOT = r"c:\Users\IKYY\Downloads\Omni\src"
fixes_applied = 0
files_fixed = 0

def log_fix(filepath, desc):
    global fixes_applied
    fixes_applied += 1

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

def fix_import_commas():
    """Remove commas after import paths in import () blocks."""
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
            
            # Fix: "package/path",  -> "package/path"  inside import blocks
            # Pattern: quoted import with trailing comma
            content = re.sub(r'(\t"[^"]+"),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Also fix single import: import "pkg",
            content = re.sub(r'(import\s+"[^"]+")\s*,\s*$', r'\1', content, flags=re.MULTILINE)
            
            if content != original:
                if write_file(fpath, content):
                    log_fix(fpath, "Fixed import commas")
                    files_fixed += 1

def fix_field_declaration_commas():
    """Remove trailing commas from struct field declarations."""
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
            lines = content.split('\n')
            new_lines = []
            in_struct = False
            brace_depth = 0
            
            for i, line in enumerate(lines):
                stripped = line.strip()
                
                # Track struct blocks
                if 'struct {' in stripped or 'struct{' in stripped:
                    in_struct = True
                    brace_depth = 0
                
                if in_struct:
                    brace_depth += stripped.count('{') - stripped.count('}')
                    if brace_depth <= 0:
                        in_struct = False
                    
                    # Remove trailing comma from struct field declarations
                    # Pattern: FieldName Type,  -> FieldName Type
                    if stripped.endswith(',') and not '(' in stripped and not ':' in stripped:
                        field_match = re.match(r'^(\s*\w+\s+\S+.*?),\s*$', line)
                        if field_match:
                            line = field_match.group(1)
                
                new_lines.append(line)
            
            content = '\n'.join(new_lines)
            
            if content != original:
                if write_file(fpath, content):
                    log_fix(fpath, "Fixed struct field commas")
                    files_fixed += 1

def fix_var_const_commas():
    """Remove trailing commas from var/const declarations that shouldn't have them."""
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
            
            # Fix: var x = value,  (standalone var, not in a group)
            content = re.sub(r'^(\s*var\s+\w+\s*=\s*.+),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: const x = value,
            content = re.sub(r'^(\s*const\s+\w+\s*=\s*.+),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: type X ...,
            content = re.sub(r'^(\s*type\s+\w+\s+.+),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix lines ending with `, where next line is a func/type declaration
            # Actually just fix any "= errors.New("...")" with trailing comma
            content = re.sub(r'(=\s*errors\.New\("[^"]*"\)),\s*$', r'\1', content, flags=re.MULTILINE)
            
            if content != original:
                if write_file(fpath, content):
                    log_fix(fpath, "Fixed var/const/type commas")
                    files_fixed += 1

def fix_assignment_commas():
    """Remove trailing commas from assignment statements."""
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
            
            # Fix: x := something,  (short var decl with comma)
            content = re.sub(r'^(\s*\w+\s*:=\s*.+\S),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: x = something,  (assignment with comma)  
            content = re.sub(r'^(\s*\w+\s*=\s*.+\S),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: _ = something, 
            content = re.sub(r'^(\s*_\s*=\s*.+\S),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: if condition {,  -> if condition {
            content = re.sub(r'^(\s*if\s+.+\{),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: for ... {,  -> for ... {
            content = re.sub(r'^(\s*for\s+.+\{),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: case ...:,  -> case ...:
            content = re.sub(r'^(\s*case\s+.+:),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: go func() {,
            content = re.sub(r'^(\s*go\s+.+\{),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: defer ...,
            content = re.sub(r'^(\s*defer\s+.+\S),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: func ... {, 
            content = re.sub(r'^(\s*func\s+.+\{),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: }(),  -> }()
            content = re.sub(r'^(\s*\}\(\)),\s*$', r'\1', content, flags=re.MULTILINE)
            
            # Fix: } else {,
            content = re.sub(r'^(\s*\}\s*else\s*\{),\s*$', r'\1', content, flags=re.MULTILINE)
            
            if content != original:
                if write_file(fpath, content):
                    log_fix(fpath, "Fixed assignment/control commas")
                    files_fixed += 1

def main():
    print("=" * 70)
    print("OMNI PHASE 3 — Fix Import/Field/Var/Assignment Commas")
    print("=" * 70)
    
    fix_import_commas()
    fix_field_declaration_commas()
    fix_var_const_commas()
    fix_assignment_commas()
    
    print(f"\nSUMMARY: {fixes_applied} fixes across {files_fixed} files")
    print("=" * 70)

if __name__ == "__main__":
    main()
