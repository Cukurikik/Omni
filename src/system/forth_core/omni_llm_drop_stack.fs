\ Omni LLM-Drop Stack (Forth)
\ System Layer: Bare-metal stack manipulation for layer dropping.

: LLM-DROP-EVAL ( depth drop_rate -- new_depth )
  \ Multiplies depth by (1 - drop_rate) assuming integer percentage (0-100)
  100 SWAP - ( depth keep_rate )
  * 100 / ;

\ Example: 24 layers, 25% drop rate -> expect 18
\ 24 25 LLM-DROP-EVAL .
