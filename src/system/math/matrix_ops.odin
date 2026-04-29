package omni_matrix

Matrix :: struct {
    rows, cols: int,
    data: []f64,
}

matrix_add :: proc(a, b: Matrix) -> (Matrix, bool) {
    if a.rows != b.rows || a.cols != b.cols {
        return Matrix{}, false
    }
    
    res := Matrix{rows = a.rows, cols = a.cols, data = make([]f64, len(a.data))}
    for i := 0; i < len(a.data); i += 1 {
        res.data[i] = a.data[i] + b.data[i]
    }
    return res, true
}
