import os

engine_dir = r"C:\Users\IKYY\Downloads\Omni\engine"

# 1. Fix main redeclared
for root, _, files in os.walk(engine_dir):
    for f in files:
        if f.endswith('.go'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            if 'func main()' in content:
                prefix = f.replace('.go', '_main').title().replace('_', '')
                content = content.replace('func main()', f'func {prefix}()')
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(content)

# 2. Fix C++ files not allowed
for root, _, files in os.walk(engine_dir):
    has_cpp_c = any(f.endswith('.cpp') or f.endswith('.c') for f in files)
    go_files = [f for f in files if f.endswith('.go')]
    if has_cpp_c and go_files:
        needs_cgo = True
        for gf in go_files:
            with open(os.path.join(root, gf), 'r', encoding='utf-8') as file:
                if 'import "C"' in file.read() or "import 'C'" in file.read():
                    needs_cgo = False
                    break
        if needs_cgo:
            path = os.path.join(root, go_files[0])
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('package '):
                    lines.insert(i+1, 'import "C"')
                    break
            with open(path, 'w', encoding='utf-8') as file:
                file.write('\n'.join(lines))

# 3. Fix bool type in hft_bridge.go
hft = os.path.join(engine_dir, 'hft', 'hft_bridge.go')
if os.path.exists(hft):
    with open(hft, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace('#include <stdint.h>', '#include <stdint.h>\n#include <stdbool.h>')
    with open(hft, 'w', encoding='utf-8') as file:
        file.write(content)

# 4. Fix time.sleep in langgraph_orchestrator.go
langgraph = os.path.join(engine_dir, 'swarm', 'langgraph_orchestrator.go')
if os.path.exists(langgraph):
    with open(langgraph, 'r', encoding='utf-8') as file:
        content = file.read()
    content = content.replace('time.sleep', 'time.Sleep')
    with open(langgraph, 'w', encoding='utf-8') as file:
        file.write(content)

print("Mass fixes for Omni compilation applied.")
