import sys, os, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestBusinessLayer(unittest.TestCase):
    def test_engine_ids_unique(self):
        from engines.engine_registry import BATCH10_ENGINES
        ids = [e["id"] for e in BATCH10_ENGINES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_engine_ids_format(self):
        from engines.engine_registry import BATCH10_ENGINES
        for e in BATCH10_ENGINES:
            self.assertTrue(e["id"].startswith("omni-"))
            self.assertTrue(e["id"].endswith("-s14b10"))
            self.assertIn("repo", e)
            self.assertIn("domain", e)

if __name__ == "__main__":
    unittest.main(verbosity=2)
