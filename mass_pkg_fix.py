import os

engine_dir = r"C:\Users\IKYY\Downloads\Omni\engine"
for root, _, files in os.walk(engine_dir):
    for f in files:
        if f.endswith('.go'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            if 'package main' in content:
                dir_name = os.path.basename(root)
                content = content.replace('package main', f'package {dir_name}')
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(content)
print("Packages renamed successfully.")
