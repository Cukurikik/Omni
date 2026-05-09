from memory import UnsafePointer
from math import add, mul

struct OmniSIMD:
    @staticmethod
    fn vector_add(ptr_a: UnsafePointer[Float32], ptr_b: UnsafePointer[Float32], ptr_res: UnsafePointer[Float32], size: Int):
        for i in range(size):
            ptr_res[i] = add(ptr_a[i], ptr_b[i])

    @staticmethod
    fn vector_mul(ptr_a: UnsafePointer[Float32], ptr_b: UnsafePointer[Float32], ptr_res: UnsafePointer[Float32], size: Int):
        for i in range(size):
            ptr_res[i] = mul(ptr_a[i], ptr_b[i])
