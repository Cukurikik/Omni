import sys
sys.path.append('.')
from src.compute.python_core.omni_advanced_programming_engine import OmniAdvancedProgrammingEngine
from src.compute.python_core.omni_base_engine import Ok, Err

def op1(x):
    return Ok(x + 1)

def op2(x):
    return Ok(x * 2)

en = OmniAdvancedProgrammingEngine()
res = en.bind_monadic_operations(5, [op1, op2])
print("IS_OK:", res.is_ok())
if not res.is_ok():
    print("ERR:", res.unwrap_err())
else:
    print("VAL:", res.value)
