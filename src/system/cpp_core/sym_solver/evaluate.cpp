/**
 * @omni-domain System Layer (Symbolic Solver)
 * @omni-source sym-math
 * @omni-description Fast C++ evaluation kernel for symbolic expressions.
 * @omni-requirement zero-mock, monadic-error
 */

#include <vector>
#include <string>
#include <stdexcept>

template<typename T>
struct OmniResult {
    bool ok;
    T value;
    std::string err;
    
    static OmniResult<T> ok_val(T v) { return {true, v, ""}; }
    static OmniResult<T> err_val(std::string e) { return {false, T{}, e}; }
};

class SymbolicKernel {
public:
    static OmniResult<double> evaluate_polynomial(const std::vector<double>& coeffs, double x) {
        if (coeffs.empty()) {
            return OmniResult<double>::err_val("Coefficients cannot be empty");
        }
        
        // Horner's method
        double result = 0.0;
        for (auto it = coeffs.rbegin(); it != coeffs.rend(); ++it) {
            result = result * x + (*it);
        }
        
        return OmniResult<double>::ok_val(result);
    }
};