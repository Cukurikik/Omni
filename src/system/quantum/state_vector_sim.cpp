#include <vector>
#include <complex>
#include <cmath>
#include <iostream>

namespace Omni {
namespace Quantum {

using ComplexDB = std::complex<double>;

template<typename T, typename E>
struct Result {
    bool is_success;
    T value;
    E error;
    static Result success(T val) { return {true, val, E()}; }
    static Result failure(E err) { return {false, T(), err}; }
};

class StateVectorSim {
private:
    std::vector<ComplexDB> state;
    size_t num_qubits;
    double inv_sqrt2;

public:
    StateVectorSim(size_t n_qubits) : num_qubits(n_qubits) {
        inv_sqrt2 = 1.0 / std::sqrt(2.0);
        size_t dim = 1ull << num_qubits;
        state.resize(dim, {0.0, 0.0});
        state[0] = {1.0, 0.0};
    }

    Result<bool, std::string> apply_hadamard(size_t target_qubit) {
        if (target_qubit >= num_qubits) return Result<bool, std::string>::failure("Target qubit out of range");
        
        size_t dim = 1ull << num_qubits;
        size_t mask = 1ull << target_qubit;
        
        for (size_t i = 0; i < dim; i++) {
            if ((i & mask) == 0) {
                size_t j = i | mask;
                ComplexDB a = state[i];
                ComplexDB b = state[j];
                
                state[i] = (a + b) * inv_sqrt2;
                state[j] = (a - b) * inv_sqrt2;
            }
        }
        return Result<bool, std::string>::success(true);
    }

    Result<bool, std::string> apply_cnot(size_t control, size_t target) {
        if (control >= num_qubits || target >= num_qubits || control == target) {
            return Result<bool, std::string>::failure("Invalid control or target qubit");
        }

        size_t dim = 1ull << num_qubits;
        size_t ctrl_mask = 1ull << control;
        size_t tgt_mask = 1ull << target;

        for (size_t i = 0; i < dim; i++) {
            if ((i & ctrl_mask) != 0 && (i & tgt_mask) == 0) {
                size_t j = i | tgt_mask;
                std::swap(state[i], state[j]);
            }
        }
        return Result<bool, std::string>::success(true);
    }

    Result<std::vector<double>, std::string> get_probabilities() const {
        std::vector<double> probs(state.size());
        for (size_t i = 0; i < state.size(); i++) {
            probs[i] = std::norm(state[i]);
        }
        return Result<std::vector<double>, std::string>::success(probs);
    }
};

}} // namespace Omni::Quantum
