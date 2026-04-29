#include <vector>
#include <stdexcept>
#include <iostream>

// OMNI IMPLICIT: CSR Matrix Operations
// C++ Compressed Sparse Row matrix format, essential for handling massive, highly sparse 
// user-item interaction datasets without blowing up RAM.
// Source: benfred/implicit

namespace omni::implicit_lib {

template<typename T>
class CSRMatrix {
private:
    std::vector<T> values;
    std::vector<int> col_indices;
    std::vector<int> row_pointers;
    int rows;
    int cols;

public:
    CSRMatrix(int r, int c) : rows(r), cols(c) {
        row_pointers.push_back(0); // Start with 0
    }

    // Builder method assuming sorted row insertions
    void add_row(const std::vector<std::pair<int, T>>& row_data) {
        for (const auto& kvp : row_data) {
            col_indices.push_back(kvp.first);
            values.push_back(kvp.second);
        }
        row_pointers.push_back(values.size());
    }

    // Sparse matrix-vector multiplication: Y = A * X
    std::vector<T> multiply(const std::vector<T>& X) const {
        if (X.size() != cols) {
            throw std::invalid_argument("Vector dimension mismatch");
        }

        std::vector<T> Y(rows, 0);
        for (int i = 0; i < rows; ++i) {
            T sum = 0;
            int row_start = row_pointers[i];
            int row_end = row_pointers[i + 1];

            for (int j = row_start; j < row_end; ++j) {
                sum += values[j] * X[col_indices[j]];
            }
            Y[i] = sum;
        }
        return Y;
    }

    int get_rows() const { return rows; }
    int get_cols() const { return cols; }
    int get_nnz() const { return values.size(); } // Number of non-zero elements
};

} // namespace omni::implicit_lib
