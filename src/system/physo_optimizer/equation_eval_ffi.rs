#[no_mangle]
pub extern "C" fn omni_eval_equation_tree(
    opcode_array: *const i32,
    val_array: *const f64,
    num_nodes: i32,
    x_input: f64,
    out_result: *mut f64,
    err_code: *mut i32,
) {
    if err_code.is_null() {
        return;
    }

    if opcode_array.is_null() || val_array.is_null() || out_result.is_null() || num_nodes <= 0 {
        unsafe { *err_code = -1 };
        return;
    }

    let opcodes = unsafe { std::slice::from_raw_parts(opcode_array, num_nodes as usize) };
    let vals = unsafe { std::slice::from_raw_parts(val_array, num_nodes as usize) };

    // Deterministic Stack-based Equation Evaluator (Reverse Polish Notation)
    // Opcodes: 0=CONST, 1=VAR_X, 2=ADD, 3=SUB, 4=MUL, 5=DIV
    
    let mut stack: Vec<f64> = Vec::with_capacity(32);

    for i in 0..(num_nodes as usize) {
        match opcodes[i] {
            0 => stack.push(vals[i]),       // Push constant
            1 => stack.push(x_input),       // Push variable X
            2 => {                          // ADD
                if stack.len() < 2 { unsafe { *err_code = -2 }; return; }
                let b = stack.pop().unwrap();
                let a = stack.pop().unwrap();
                stack.push(a + b);
            },
            3 => {                          // SUB
                if stack.len() < 2 { unsafe { *err_code = -2 }; return; }
                let b = stack.pop().unwrap();
                let a = stack.pop().unwrap();
                stack.push(a - b);
            },
            4 => {                          // MUL
                if stack.len() < 2 { unsafe { *err_code = -2 }; return; }
                let b = stack.pop().unwrap();
                let a = stack.pop().unwrap();
                stack.push(a * b);
            },
            5 => {                          // DIV
                if stack.len() < 2 { unsafe { *err_code = -2 }; return; }
                let b = stack.pop().unwrap();
                let a = stack.pop().unwrap();
                if b.abs() < 1e-10 { unsafe { *err_code = -3; *out_result = 0.0 }; return; } // Div by zero
                stack.push(a / b);
            },
            _ => { unsafe { *err_code = -4 }; return; } // Invalid opcode
        }
    }

    if stack.len() != 1 {
        unsafe { *err_code = -5 }; // Invalid tree structure, stack not reduced to 1
        return;
    }

    unsafe { 
        *out_result = stack[0];
        *err_code = 0; 
    };
}
