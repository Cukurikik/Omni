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

def fix_composite_literal_commas(content):
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        if stripped.endswith(',,'):
            line = line.rstrip().rstrip(',') + ','
            stripped = line.strip()
            
        if ',,' in stripped:
             line = line.replace(',,', ',')
             stripped = line.strip()
             
        if re.match(r'^\s*"[^"]+"\s*:.*$', line):
            if not stripped.endswith(',') and not stripped.endswith('{') and not stripped.endswith('}') and not stripped.endswith('*/'):
                line = line.rstrip() + ','
                
        if re.match(r'^\s*[A-Z][a-zA-Z0-9_]*\s*:.*$', line) and not line.startswith('//'):
            if not stripped.endswith(',') and not stripped.endswith('{') and not stripped.endswith('}') and not stripped.endswith('*/'):
                if not stripped.startswith('case ') and not stripped.startswith('default:'):
                    line = line.rstrip() + ','
                    
        new_lines.append(line)
        
    content = '\n'.join(new_lines)
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
            content = fix_composite_literal_commas(content)
            
            content = content.replace("Error: &", "Err: &")
            content = content.replace("Error: ctx.Err()", "Err: ctx.Err()")
            content = content.replace("Error: err", "Err: err")
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

fix_all_files()
print(f"SUMMARY: {fixes_applied} fixes across {files_fixed} files")
