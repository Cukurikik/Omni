import os
import re

def repair_metadata():
    engine_root = "c:/Users/IKYY/Downloads/Omni"
    count = 0
    pattern = re.compile(r"^omni_[\w]+_engine\.(py|ts|js|rs|go|kt|swift|cpp)$")
    
    for root, dirs, files in os.walk(engine_root):
        if "node_modules" in root or ".git" in root or "venv" in root:
            continue
            
        for file in files:
            if pattern.match(file):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    modified = False
                    if "ENGINE_VERSION" not in content and file.endswith(".py"):
                        content = f'ENGINE_VERSION = "1.0.0-omni"\n' + content
                        modified = True
                        
                    if modified:
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(content)
                        count += 1
                except Exception as e:
                    print(f"Error on {path}: {e}")
                    
    print(f"Mass metadata repair completed. Patched {count} engines.")

if __name__ == "__main__":
    repair_metadata()
