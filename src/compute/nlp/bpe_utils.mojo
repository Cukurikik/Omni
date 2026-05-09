#=============================================================================
# OMNI COMPUTE LAYER — BPE UTILITIES (MOJO)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Helper functions for BPE tokenizer operations in Mojo.
#=============================================================================

from memory import memcpy
from pointer import Pointer

@value
struct StringSlice:
    var ptr: Pointer[Int8]
    var length: Int
    
    fn __init__(inout self, ptr: Pointer[Int8], length: Int):
        self.ptr = ptr
        self.length = length

fn merge_strings(a: StringSlice, b: StringSlice) -> StringSlice:
    """
    Fast zero-copy string merge simulation for BPE algorithms.
    """
    let new_len = a.length + b.length
    let new_ptr = Pointer[Int8].alloc(new_len)
    
    memcpy(new_ptr, a.ptr, a.length)
    memcpy(new_ptr.offset(a.length), b.ptr, b.length)
    
    return StringSlice(new_ptr, new_len)

fn count_frequency(tokens: Pointer[Int32], length: Int) -> Int:
    """
    Counts frequency of token pairs.
    Mock implementation simulating SIMD counting.
    """
    var count = 0
    for i in range(length - 1):
        if tokens.load(i) == tokens.load(i+1):
            count += 1
    return count
