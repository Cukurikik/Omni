import os

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

def fix_premature_braces_perfect(content):
    lines = content.split('\n')
    changed = True
    iterations = 0
    
    top_level_keywords = ('func ', 'type ', 'var ', 'const ', 'import ', 'package ', 'import(')
    
    while changed and iterations < 15:
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
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].strip()
                    if not next_line or next_line.startswith('//') or next_line.startswith('/*') or next_line.startswith('*'):
                        continue
                    
                    if not next_line.startswith(top_level_keywords) and next_line != ')' and not next_line.startswith('var(') and not next_line.startswith('const('):
                        # check if next line is `}` 
                        if next_line != '}':
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
            content = fix_premature_braces_perfect(content)
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

fix_all_files()
print(f"SUMMARY: {fixes_applied} fixes across {files_fixed} files")
