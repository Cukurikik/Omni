import os
import glob
import py_compile

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'

files = glob.glob(os.path.join(TARGET_DIR, 'omni_*_engine.py'))
bad_files = []

for f in files:
    try:
        py_compile.compile(f, doraise=True)
    except py_compile.PyCompileError as e:
        bad_files.append((f, str(e)))

print(f"Total files with compile errors: {len(bad_files)}")
print("First 10 bad files:")
for bf, err in bad_files[:10]:
    print(bf)
    print(err)
    print("---")
