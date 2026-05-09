(module
  (memory (export "memory") 1)
  
  ;; Simple XOR cipher for fast obfuscation in WASM
  (func $xor_cipher (export "xor_cipher") (param $ptr i32) (param $len i32) (param $key i32)
    (local $i i32)
    (local.set $i (i32.const 0))
    (block
      (loop
        (br_if 1 (i32.eq (local.get $i) (local.get $len)))
        
        ;; Read byte, XOR with key, write back
        (i32.store8
          (i32.add (local.get $ptr) (local.get $i))
          (i32.xor
            (i32.load8_u (i32.add (local.get $ptr) (local.get $i)))
            (local.get $key)
          )
        )
        
        (local.set $i (i32.add (local.get $i) (i32.const 1)))
        (br 0)
      )
    )
  )
)
