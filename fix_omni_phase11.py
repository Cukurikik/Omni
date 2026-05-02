#!/usr/bin/env python3
"""
OMNI Phase 11 — Deep fix for remaining commas and structural issues.

Targets:
1. Arithmetic/expression trailing commas: x += y * z,
2. Channel send trailing commas: ch <- value,
3. More premature brace closings (re-run with improved heuristics)
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

def fix_expression_commas():
    """Remove trailing commas from expressions, assignments, and channel sends."""
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
                    remove = False
                    
                    # Arithmetic: x += y, or x -= y, or x *= y, etc.
                    if re.match(r'^\s*\w[\w.\[\]]*\s*[+\-*/&|^%]?=\s*.+,$', line):
                        # But NOT struct field assignment like: Field: value,
                        if ':' not in stripped.split('=')[0]:
                            remove = True
                    
                    # Channel send: ch <- value,
                    if '<-' in stripped and stripped.endswith(','):
                        remove = True
                    
                    # Function call with trailing comma
                    if re.search(r'\w+\([^)]*\)\s*,$', stripped) and ':' not in stripped.split('(')[0]:
                        remove = True
                    
                    # close(x), or make(x),
                    if re.match(r'^\s*(close|make|delete|copy|len|cap)\(.*\)\s*,$', line):
                        remove = True
                    
                    # if/for/switch with trailing comma
                    if re.match(r'^\s*(if|for|switch|select|case|default)\b.*,$', line):
                        remove = True
                    
                    # Simple expressions: someVar++ or someVar-- with comma
                    if re.match(r'^\s*\w[\w.]*(\+\+|--)\s*,$', line):
                        remove = True
                    
                    # return statements
                    if stripped.startswith('return ') and stripped.endswith(','):
                        remove = True
                    
                    # panic/defer/go
                    if stripped.startswith(('panic(', 'defer ', 'go ')):
                        remove = True
                    
                    # Blank continue/break with comma
                    if stripped in ('continue,', 'break,'):
                        remove = True
                    
                    if remove:
                        line = line.rstrip().rstrip(',')
                
                new_lines.append(line)
            
            content = '\n'.join(new_lines)
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

def fix_premature_braces_v2():
    """Fix premature closing braces — improved version that handles more patterns."""
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
            changed = True
            iterations = 0
            
            while changed and iterations < 5:
                changed = False
                iterations += 1
                new_lines = []
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    
                    # Check if this is a lone } followed by indented code
                    if stripped == '}' and i + 1 < len(lines):
                        # Count braces up to this point
                        depth = 0
                        for j in range(i + 1):
                            for ch in lines[j]:
                                if ch == '{':
                                    depth += 1
                                elif ch == '}':
                                    depth -= 1
                        
                        if depth < 0:
                            # This } makes braces go negative — there's an extra }
                            # Check if there's indented code below
                            has_indented_below = False
                            for k in range(i + 1, min(i + 10, len(lines))):
                                ks = lines[k].strip()
                                if ks == '':
                                    continue
                                if lines[k].startswith('\t\t') or lines[k].startswith('    '):
                                    has_indented_below = True
                                break
                            
                            if has_indented_below:
                                # Skip this premature }
                                changed = True
                                continue
                    
                    new_lines.append(line)
                
                lines = new_lines
            
            content = '\n'.join(lines)
            
            # Ensure brace balance (add closing braces at end if needed)
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
    print("OMNI PHASE 11 — Deep Expression Comma + Brace Fix")
    print("=" * 70)
    
    print("\n[1] Fixing expression/channel/statement commas...")
    fix_expression_commas()
    
    print("[2] Fixing premature braces v2...")
    fix_premature_braces_v2()
    
    print(f"\nSUMMARY: {fixes_applied} fixes across {files_fixed} files")
    print("=" * 70)

if __name__ == "__main__":
    main()
