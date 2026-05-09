⍝ OMNI APL Array Operations for High-Density Tensor Manipulation

⍝ Sigmoid activation function
Sigmoid ← {1 ÷ 1 + * -⍵}

⍝ Matrix Multiplication (Dot Product)
DotProduct ← {⍺ +.× ⍵}

⍝ Example Neural Network Forward Pass (Single Layer)
⍝ W is weight matrix, X is input vector, B is bias
ForwardPass ← {Sigmoid B + W DotProduct X}
