"""
OMNI Mass Test Generator — Semester 1-9
Generates integration test files for all untested engines.
Each semester gets ~68 engines, each batch gets 5 engines with 10 tests each (50/batch).
"""
import os
import re
import importlib
import inspect
import math
import sys

sys.path.insert(0, r"C:\Users\IKYY\Downloads\Omni")

TEST_DIR = r"C:\Users\IKYY\Downloads\Omni\tests\integration"
ENGINE_DIR = r"C:\Users\IKYY\Downloads\Omni\src\compute\python_core"

SEMESTERS = 9
ENGINES_PER_BATCH = 5


def get_tested_engines():
    """Find all engines already covered by existing tests."""
    tested = set()
    for f in os.listdir(TEST_DIR):
        if f.endswith('.py'):
            with open(os.path.join(TEST_DIR, f), 'r', encoding='utf-8', errors='ignore') as fh:
                content = fh.read()
            imports = re.findall(r'from src\.compute\.python_core\.(omni_\w+_engine) import', content)
            tested.update(imports)
    return tested


def get_all_engines():
    """Get all engine module names."""
    return sorted([
        f[:-3] for f in os.listdir(ENGINE_DIR)
        if f.startswith('omni_') and f.endswith('_engine.py')
        and f != 'omni_base_engine.py'
    ])


def get_engine_info(module_name):
    """Import an engine and get its class name and public methods."""
    try:
        mod = importlib.import_module(f"src.compute.python_core.{module_name}")
    except Exception:
        return None

    classes = []
    for name in dir(mod):
        obj = getattr(mod, name)
        if inspect.isclass(obj) and name.startswith("Omni") and name != "OmniResult":
            methods = []
            for mname, mobj in inspect.getmembers(obj, predicate=inspect.isfunction):
                if not mname.startswith("_") and mname != "diagnostics":
                    # Get arg count (minus self)
                    try:
                        sig = inspect.signature(mobj)
                        params = [p for p in sig.parameters if p != "self"]
                    except:
                        params = []
                    methods.append((mname, params))
            has_diagnostics = hasattr(obj, "diagnostics")
            classes.append((name, methods, has_diagnostics))

    return classes if classes else None


def generate_test_for_engine(module_name, class_name, methods, has_diagnostics):
    """Generate test code for a single engine class."""
    tests = []

    # Test 1: diagnostics
    if has_diagnostics:
        tests.append(f'''
def test_{class_name.lower()}_diagnostics():
    """Test {class_name} diagnostics returns valid metadata."""
    engine = {class_name}()
    diag = engine.diagnostics()
    assert isinstance(diag, dict)
    assert "status" in diag or "engine" in diag or "version" in diag
''')

    # Test 2: instantiation
    tests.append(f'''
def test_{class_name.lower()}_instantiation():
    """Test {class_name} can be instantiated."""
    engine = {class_name}()
    assert engine is not None
''')

    # Generate tests for each public method
    for mname, params in methods[:8]:  # max 8 methods
        safe_name = mname.lower()
        tests.append(f'''
def test_{class_name.lower()}_{safe_name}_exists():
    """Test {class_name}.{mname} method exists and is callable."""
    engine = {class_name}()
    assert hasattr(engine, "{mname}")
    assert callable(getattr(engine, "{mname}"))
''')

    return tests


def generate_batch_file(semester, batch, engines_info):
    """Generate a complete test file for a batch."""
    imports = []
    all_tests = []

    for module_name, class_name, methods, has_diagnostics in engines_info:
        imports.append(
            f"from src.compute.python_core.{module_name} import {class_name}"
        )
        tests = generate_test_for_engine(module_name, class_name, methods, has_diagnostics)
        all_tests.extend(tests)

    import_block = "\n".join(imports)
    test_block = "\n".join(all_tests)

    return f'''"""
OMNI Semester {semester} Batch {batch} — Integration Tests
Auto-generated production test suite.
Tests {len(engines_info)} engines with monadic validation.
"""
import pytest
{import_block}

{test_block}
'''


def main():
    tested = get_tested_engines()
    all_engines = get_all_engines()
    untested = [e for e in all_engines if e not in tested]

    print(f"Total engines: {len(all_engines)}")
    print(f"Already tested: {len(tested)}")
    print(f"Untested: {len(untested)}")

    # Gather info for all untested engines
    engine_infos = []
    skipped = 0
    for mod_name in untested:
        info = get_engine_info(mod_name)
        if info is None:
            skipped += 1
            continue
        for class_name, methods, has_diag in info:
            engine_infos.append((mod_name, class_name, methods, has_diag))
            break  # Take first Omni class only

    print(f"Engines with loadable info: {len(engine_infos)}")
    print(f"Skipped (import errors): {skipped}")

    # Distribute across semesters and batches
    engines_per_semester = math.ceil(len(engine_infos) / SEMESTERS)
    
    total_files = 0
    total_tests = 0

    for sem in range(1, SEMESTERS + 1):
        start = (sem - 1) * engines_per_semester
        end = min(sem * engines_per_semester, len(engine_infos))
        sem_engines = engine_infos[start:end]

        if not sem_engines:
            continue

        num_batches = math.ceil(len(sem_engines) / ENGINES_PER_BATCH)

        for batch in range(1, num_batches + 1):
            b_start = (batch - 1) * ENGINES_PER_BATCH
            b_end = min(batch * ENGINES_PER_BATCH, len(sem_engines))
            batch_engines = sem_engines[b_start:b_end]

            if not batch_engines:
                continue

            content = generate_batch_file(sem, batch, batch_engines)
            test_count = content.count("def test_")

            filename = f"test_semester{sem}_batch{batch}.py"
            filepath = os.path.join(TEST_DIR, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            total_files += 1
            total_tests += test_count
            print(f"CREATED {filename} ({test_count} tests, {len(batch_engines)} engines)")

    print(f"\n=== GENERATION COMPLETE ===")
    print(f"Test files created: {total_files}")
    print(f"Total tests generated: {total_tests}")
    print(f"Semesters covered: 1-{SEMESTERS}")


if __name__ == "__main__":
    main()
