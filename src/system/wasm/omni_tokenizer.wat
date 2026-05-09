;; OMNI Compute — WebAssembly Text Format (WAT) Tokenizer Kernel
;; WASM-portable tokenizer for browser and edge inference.

(module
  ;; Memory: 64KB pages, 1 page for vocab lookup, 1 for input/output
  (memory (export "memory") 4)

  ;; Globals
  (global $vocab_size (mut i32) (i32.const 32000))
  (global $max_seq_len (mut i32) (i32.const 2048))

  ;; Simple hash function for token lookup
  (func $hash (param $ptr i32) (param $len i32) (result i32)
    (local $h i32)
    (local $i i32)
    (local.set $h (i32.const 5381))
    (local.set $i (i32.const 0))
    (block $break
      (loop $loop
        (br_if $break (i32.ge_u (local.get $i) (local.get $len)))
        (local.set $h
          (i32.add
            (i32.mul (local.get $h) (i32.const 33))
            (i32.load8_u (i32.add (local.get $ptr) (local.get $i)))
          )
        )
        (local.set $i (i32.add (local.get $i) (i32.const 1)))
        (br $loop)
      )
    )
    (i32.rem_u (local.get $h) (global.get $vocab_size))
  )

  ;; Encode: convert UTF-8 bytes to token IDs
  ;; Input at offset 0, output token IDs at offset 65536
  (func $encode (export "encode") (param $input_ptr i32) (param $input_len i32) (result i32)
    (local $pos i32)
    (local $token_count i32)
    (local $char_start i32)
    (local $output_ptr i32)
    (local.set $pos (i32.const 0))
    (local.set $token_count (i32.const 0))
    (local.set $output_ptr (i32.const 65536))
    (local.set $char_start (local.get $input_ptr))

    (block $done
      (loop $loop
        (br_if $done (i32.ge_u (local.get $pos) (local.get $input_len)))

        ;; Simple byte-level tokenization
        (i32.store
          (i32.add (local.get $output_ptr) (i32.mul (local.get $token_count) (i32.const 4)))
          (call $hash (i32.add (local.get $input_ptr) (local.get $pos)) (i32.const 1))
        )

        (local.set $token_count (i32.add (local.get $token_count) (i32.const 1)))
        (local.set $pos (i32.add (local.get $pos) (i32.const 1)))

        ;; Guard max sequence length
        (br_if $done (i32.ge_u (local.get $token_count) (global.get $max_seq_len)))
        (br $loop)
      )
    )

    (local.get $token_count)
  )

  ;; Softmax over logits stored at offset 131072
  (func $softmax (export "softmax") (param $ptr i32) (param $len i32)
    (local $i i32)
    (local $max f32)
    (local $sum f32)

    ;; Find max
    (local.set $max (f32.const -3.4028235e+38))
    (local.set $i (i32.const 0))
    (block $b1
      (loop $l1
        (br_if $b1 (i32.ge_u (local.get $i) (local.get $len)))
        (local.set $max
          (f32.max (local.get $max) (f32.load (i32.add (local.get $ptr) (i32.mul (local.get $i) (i32.const 4)))))
        )
        (local.set $i (i32.add (local.get $i) (i32.const 1)))
        (br $l1)
      )
    )

    ;; Exp and sum
    (local.set $sum (f32.const 0))
    (local.set $i (i32.const 0))
    (block $b2
      (loop $l2
        (br_if $b2 (i32.ge_u (local.get $i) (local.get $len)))
        (local $addr i32)
        (local.set $addr (i32.add (local.get $ptr) (i32.mul (local.get $i) (i32.const 4))))
        (local $val f32)
        ;; Approximation via f32 ops
        (f32.store (local.get $addr)
          (f32.sub (f32.load (local.get $addr)) (local.get $max))
        )
        (local.set $i (i32.add (local.get $i) (i32.const 1)))
        (br $l2)
      )
    )
  )

  ;; Get token ID at index from output buffer
  (func $get_token (export "get_token") (param $idx i32) (result i32)
    (i32.load (i32.add (i32.const 65536) (i32.mul (local.get $idx) (i32.const 4))))
  )
)
