from typing import TypeVar, Generic
from omni.core import Result, Ok, Err
from omni.system import zero_copy

T = TypeVar('T')

def allocate_tensor_pages(size_bytes: int) -> Result[zero_copy.Buffer, Exception]:
    """Allocates paged memory for VLLM attention blocks natively using OMNI zero-copy."""
    try:
        buffer = zero_copy.alloc(size_bytes)
        return Ok(buffer)
    except Exception as e:
        return Err(e)
