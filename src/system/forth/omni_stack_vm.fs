\ OMNI Forth Stack Virtual Machine Engine
\ Minimal footprint for deeply embedded systems

: OMNI-INIT ( -- )
  ." OMNI Forth VM Initialized." CR ;

: MAC-OP ( n1 n2 acc -- acc' )
  \ Multiply and accumulate
  >R * R> + ;

: TENSOR-DOT-PRODUCT ( addr1 addr2 len -- result )
  0 >R \ Initialize accumulator
  0 DO
    OVER I CELLS + @  \ Fetch A[i]
    OVER I CELLS + @  \ Fetch B[i]
    R> MAC-OP >R      \ Multiply and add to acc
  LOOP
  DROP DROP R> ;      \ Clean stack and return result

OMNI-INIT
