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

def fix_struct_type_commas(content):
    lines = content.split('\n')
    new_lines = []
    in_struct = False
    struct_depth = 0
    
    for line in lines:
        stripped = line.strip()
        if re.match(r'^\s*type\s+\w+\s+struct\s*\{', line):
            in_struct = True
            struct_depth = 1
            new_lines.append(line)
            continue
            
        if in_struct:
            struct_depth += line.count('{') - line.count('}')
            if struct_depth <= 0:
                in_struct = False
            else:
                if stripped.endswith(','):
                    if ':' not in stripped or re.search(r'`.*:.*`', stripped):
                        line = line.rstrip().rstrip(',')
        
        new_lines.append(line)
    return '\n'.join(new_lines)

def fix_premature_braces(content):
    lines = content.split('\n')
    changed = True
    iterations = 0
    
    while changed and iterations < 10:
        changed = False
        iterations += 1
        new_lines = []
        depth = 0
        
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            depth_before = depth
            depth += line.count('{') - line.count('}')
            
            if stripped == '}' and depth == 0:
                is_premature = False
                for j in range(i + 1, min(i + 20, len(lines))):
                    next_line = lines[j].strip()
                    if not next_line or next_line.startswith('//'):
                        continue
                    
                    if (next_line.startswith('if ') or 
                        next_line.startswith('return ') or 
                        next_line.startswith('for ') or
                        ':=' in next_line or
                        (next_line.startswith('var ') and depth_before > 1) or
                        next_line.startswith('switch ') or
                        next_line.startswith('fmt.') or
                        next_line.startswith('ch <-') or
                        next_line.startswith('go ') or
                        next_line.startswith('defer ')):
                        is_premature = True
                    break
                
                if is_premature:
                    changed = True
                    depth = depth_before
                    i += 1
                    continue
            
            new_lines.append(line)
            i += 1
            
        lines = new_lines
    
    depth = 0
    new_lines = []
    for line in lines:
        stripped = line.strip()
        new_depth = depth + line.count('{') - line.count('}')
        if new_depth < 0 and stripped == '}':
            continue
        depth = new_depth
        new_lines.append(line)
        
    lines = new_lines
    content = '\n'.join(lines)
    
    open_count = content.count('{')
    close_count = content.count('}')
    if open_count > close_count:
        content = content.rstrip() + '\n'
        for _ in range(open_count - close_count):
            content += '}\n'
            
    return content

def fix_all_files():
    global fixes_applied, files_fixed
    for root, dirs, files in os.walk(OMNI_ROOT):
        for fname in files:
            if not fname.endswith('.go'):
                continue
            fpath = os.path.join(root, fname)
            content = read_file(fpath)
            if not content: continue
            
            original = content
            content = fix_struct_type_commas(content)
            content = fix_premature_braces(content)
            
            content = re.sub(r'^\s*return\s+.*,\s*$', lambda m: m.group(0).rstrip().rstrip(','), content, flags=re.MULTILINE)
            content = re.sub(r'^\s*[\w.]+\([^)]*\),\s*$', lambda m: m.group(0).rstrip().rstrip(','), content, flags=re.MULTILINE)
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

fix_all_files()
print(f"SUMMARY: {fixes_applied} fixes across {files_fixed} files")
