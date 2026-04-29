import unittest
from engine_registry import register_batch_12

class TestIntegrationBatch12(unittest.TestCase):
    def test_registry_integration(self):
        res = register_batch_12()
        self.assertTrue(res.is_ok)
        self.assertIsNotNone(res.value)
        self.assertEqual(len(res.value), 17)
        
    def test_zero_mock_compliance(self):
        res = register_batch_12()
        for engine, path in res.value:
            self.assertNotIn("mock", path.lower())

if __name__ == '__main__':
    unittest.main()
