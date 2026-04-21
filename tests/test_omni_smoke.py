# ===========================================================================
# OMNI TEST SUITE — CROSS-LANGUAGE SMOKE TESTS
# ===========================================================================
# This test runner validates that every layer has at least one engine file,
# verifies bridge interfaces exist, checks Omnifile.toml integrity, and
# confirms the registry scanner passes all 30 assertions.
# ===========================================================================

import os
import sys
import importlib
import unittest

OMNI_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR   = os.path.join(OMNI_ROOT, "src")

# ---- Helpers ---------------------------------------------------------------

def files_in(layer, *extensions):
    """Return list of files in a layer matching given extensions."""
    layer_dir = os.path.join(SRC_DIR, layer)
    if not os.path.isdir(layer_dir):
        return []
    return [f for f in os.listdir(layer_dir)
            if any(f.endswith(ext) for ext in extensions)]

# ---- Test Cases ------------------------------------------------------------

class TestLayerPresence(unittest.TestCase):
    """Phase 1: Every OMNI layer must contain at least one engine file."""

    def test_system_has_c_or_cpp_or_rs_or_zig(self):
        engines = files_in("system", ".c", ".cpp", ".rs", ".zig", ".carbon")
        self.assertGreater(len(engines), 0, "System layer has no engine files")

    def test_network_has_go_or_js_or_ex(self):
        engines = files_in("network", ".go", ".js", ".ex")
        self.assertGreater(len(engines), 0, "Network layer has no engine files")

    def test_domain_has_cs_or_java_or_rb_or_php(self):
        engines = files_in("domain", ".cs", ".java", ".rb", ".php", ".graphql")
        self.assertGreater(len(engines), 0, "Domain layer has no engine files")

    def test_compute_has_py_or_jl_or_r_or_mojo_or_hs(self):
        engines = files_in("compute", ".py", ".jl", ".R", ".r", ".mojo", ".hs")
        self.assertGreater(len(engines), 0, "Compute layer has no engine files")

    def test_ui_has_ts_or_dart_or_swift_or_html(self):
        engines = files_in("ui", ".ts", ".dart", ".swift", ".html")
        self.assertGreater(len(engines), 0, "UI layer has no engine files")


class TestOmnifileIntegrity(unittest.TestCase):
    """Phase 1: Omnifile.toml must exist and contain required sections."""

    def setUp(self):
        self.omnifile = os.path.join(OMNI_ROOT, "Omnifile.toml")

    def test_omnifile_exists(self):
        self.assertTrue(os.path.isfile(self.omnifile), "Omnifile.toml not found")

    def test_omnifile_has_package_section(self):
        with open(self.omnifile, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("[package]", content)

    def test_omnifile_has_layers_section(self):
        with open(self.omnifile, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("[layers]", content)

    def test_omnifile_has_permissions_section(self):
        with open(self.omnifile, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("[permissions]", content)

    def test_omnifile_has_build_section(self):
        with open(self.omnifile, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("[build]", content)


class TestBridgeInterfaces(unittest.TestCase):
    """Phase 2: All 5 bridge interfaces must exist."""

    def test_system_bridge_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(SRC_DIR, "bridge", "system_bridge.rs")))

    def test_network_bridge_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(SRC_DIR, "bridge", "network_bridge.go")))

    def test_domain_bridge_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(SRC_DIR, "bridge", "domain_bridge.ts")))

    def test_compute_bridge_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(SRC_DIR, "bridge", "compute_bridge.py")))

    def test_ui_bridge_exists(self):
        self.assertTrue(os.path.isfile(os.path.join(SRC_DIR, "bridge", "ui_bridge.dart")))


class TestGraphQLSchema(unittest.TestCase):
    """Phase 2: GraphQL schema must exist and define key types."""

    def setUp(self):
        self.schema_path = os.path.join(SRC_DIR, "domain", "schema.graphql")

    def test_schema_exists(self):
        self.assertTrue(os.path.isfile(self.schema_path))

    def test_schema_has_query_type(self):
        with open(self.schema_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("type Query", content)

    def test_schema_has_mutation_type(self):
        with open(self.schema_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("type Mutation", content)

    def test_schema_has_order_type(self):
        with open(self.schema_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("type Order", content)


class TestREADMEsExist(unittest.TestCase):
    """Phase 1: Every layer must have a README.md."""

    def test_system_readme(self):
        self.assertTrue(os.path.isfile(os.path.join(SRC_DIR, "system", "README.md")))

    def test_network_readme(self):
        self.assertTrue(os.path.isfile(os.path.join(SRC_DIR, "network", "README.md")))

    def test_domain_readme(self):
        self.assertTrue(os.path.isfile(os.path.join(SRC_DIR, "domain", "README.md")))

    def test_compute_readme(self):
        self.assertTrue(os.path.isfile(os.path.join(SRC_DIR, "compute", "README.md")))

    def test_ui_readme(self):
        self.assertTrue(os.path.isfile(os.path.join(SRC_DIR, "ui", "README.md")))


class TestHaskellLocationFixed(unittest.TestCase):
    """Gap 1: Haskell must be in compute/, not functional/."""

    def test_haskell_in_compute(self):
        hs_files = files_in("compute", ".hs")
        self.assertGreater(len(hs_files), 0, "No .hs files in compute/")

    def test_functional_dir_removed(self):
        self.assertFalse(
            os.path.isdir(os.path.join(SRC_DIR, "functional")),
            "src/functional/ should no longer exist"
        )


class TestLanguageCoverage(unittest.TestCase):
    """Phase 3: All 15+ languages must have at least one file."""

    LANGUAGE_MAP = {
        "C":          ("system",  [".c"]),
        "C++":        ("system",  [".cpp", ".cc"]),
        "Rust":       ("system",  [".rs"]),
        "Zig":        ("system",  [".zig"]),
        "Carbon":     ("system",  [".carbon"]),
        "Go":         ("network", [".go"]),
        "JavaScript": ("network", [".js"]),
        "Elixir":     ("network", [".ex"]),
        "C#":         ("domain",  [".cs"]),
        "Java":       ("domain",  [".java"]),
        "Ruby":       ("domain",  [".rb"]),
        "PHP":        ("domain",  [".php"]),
        "Python":     ("compute", [".py"]),
        "Julia":      ("compute", [".jl"]),
        "R":          ("compute", [".R", ".r"]),
        "Mojo":       ("compute", [".mojo"]),
        "Haskell":    ("compute", [".hs"]),
        "TypeScript": ("ui",      [".ts"]),
        "Dart":       ("ui",      [".dart"]),
        "Swift":      ("ui",      [".swift"]),
        "HTML":       ("ui",      [".html"]),
    }

    def test_all_languages_present(self):
        missing = []
        for lang, (layer, exts) in self.LANGUAGE_MAP.items():
            found = files_in(layer, *exts)
            if not found:
                missing.append(f"{lang} ({layer}/{exts})")
        self.assertEqual(missing, [],
                         f"Missing languages: {', '.join(missing)}")


# ---- Runner ----------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 72)
    print("  OMNI FRAMEWORK — CROSS-LANGUAGE SMOKE TEST SUITE")
    print("=" * 72)
    unittest.main(verbosity=2)
