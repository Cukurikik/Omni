import unittest
from .tensor_allocator import allocate_tensor_pages

class TestTensorAllocator(unittest.TestCase):
    def test_allocation_success(self):
        res = allocate_tensor_pages(1024)
        self.assertTrue(res.is_ok())
        self.assertIsNotNone(res.unwrap())
