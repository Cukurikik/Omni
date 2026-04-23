import os, glob, py_compile

TARGET_DIR = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core'
CANONICAL = 'from src.compute.python_core.omni_base_engine import Result, Ok, Err'

broken = [
    "omni_async_generator_engine.py",
    "omni_hanoi_rainbow_engine.py",
    "omni_object_detection_engine.py",
    "omni_signal_router_engine.py",
    "omni_skills_web_dev_engine.py",
    "omni_u3d_unity_engine.py",
]

for bn in broken:
    f = os.path.join(TARGET_DIR, bn)
    with open(f, 'r', encoding='utf-8') as fh:
        lines = fh.readlines()
    
    # Remove ALL canonical import lines first
    cleaned = [l for l in lines if CANONICAL not in l]
    
    # Find the best insertion point: after all imports, before first class/def
    insert_idx = 0
    in_docstring = False
    docstring_char = None
    
    for i, line in enumerate(cleaned):
        stripped = line.strip()
        
        # Track docstrings
        if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
            docstring_char = stripped[:3]
            if stripped.count(docstring_char) >= 2:
                insert_idx = i + 1
            else:
                in_docstring = True
            continue
        
        if in_docstring:
            if docstring_char and docstring_char in stripped:
                in_docstring = False
                insert_idx = i + 1
            continue
        
        first_char = line[0:1] if line else ''
        if first_char not in (' ', '\t', '\r', '\n', ''):
            if stripped.startswith('from ') or stripped.startswith('import ') or stripped.startswith('#') or stripped == '' or stripped.startswith('ENGINE_'):
                insert_idx = i + 1
            elif stripped.startswith('class ') or stripped.startswith('def ') or stripped.startswith('@'):
                break
    
    cleaned.insert(insert_idx, CANONICAL + '\n')
    
    with open(f, 'w', encoding='utf-8') as fh:
        fh.writelines(cleaned)
    
    try:
        py_compile.compile(f, doraise=True)
        print(f"  FIXED: {bn}")
    except py_compile.PyCompileError as e:
        print(f"  STILL BROKEN: {bn}: {str(e)[:100]}")
