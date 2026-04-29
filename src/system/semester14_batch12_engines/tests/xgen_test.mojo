from sequence_attention import compute_8k_attention

fn main():
    print("Testing Xgen 8k Sequence Attention Engine...")
    
    var q = Tensor[DType.float32](8192, 128)
    var k = Tensor[DType.float32](8192, 128)
    var v = Tensor[DType.float32](8192, 128)
    
    let res = compute_8k_attention(q, k, v)
    if res.is_ok:
        print("PASS: Attention output generated successfully.")
    else:
        print("FAIL: " + res.error)
