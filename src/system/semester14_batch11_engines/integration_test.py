import unittest
from engine_registry import register_all_engines

class TestIntegrationBatch11(unittest.TestCase):
    def test_registry_integration(self):
        res = register_all_engines()
        self.assertTrue(res.is_ok)
        self.assertIsNotNone(res.value)
        self.assertEqual(len(res.value), 19)
        
    def test_zero_mock_compliance(self):
        res = register_all_engines()
        for engine, path in res.value:
            self.assertNotIn("mock", path.lower())

if __name__ == '__main__':
    unittest.main()
