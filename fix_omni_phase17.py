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
            
            # replace Result with OmniResult where it is used as a type or literal
            # `) Result {` -> `) OmniResult {`
            content = re.sub(r'\)\s*Result\s*\{', ') OmniResult {', content)
            # `Result{` -> `OmniResult{`
            content = re.sub(r'\bResult\s*\{', 'OmniResult{', content)
            
            if 'omni_dvc_data_versioning.go' in fname:
                # move imports to the top
                if 'import (' in content:
                    imports_block = re.search(r'import\s*\([\s\S]*?\)', content)
                    if imports_block:
                        imp = imports_block.group(0)
                        content = content.replace(imp, '')
                        content = re.sub(r'(package\s+\w+\s*)', r'\1\n\n' + imp + '\n', content)
            
            if 'gpu_task_queue.go' in fname:
                content = content.replace('return Result{nil, &GPUQueueError{Msg: "Ghost memory mapping (Bytes allocated without active tasks)"}}', 'return OmniResult{nil, &GPUQueueError{Msg: "Ghost memory mapping (Bytes allocated without active tasks)"}}\n\t}')

            if 'bio_swarm_router.go' in fname or 'cogelot_agent_thread.go' in fname or 'multimodal_toolkit_bus.go' in fname:
                content = content.replace('Result{', 'OmniResult{')
                content = content.replace(') Result {', ') OmniResult {')
            
            if content != original:
                if write_file(fpath, content):
                    fixes_applied += 1
                    files_fixed += 1

fix_all_files()
print(f"SUMMARY: {fixes_applied} fixes across {files_fixed} files")
