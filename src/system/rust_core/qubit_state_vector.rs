/// OMNI Qubit State Vector
/// High-performance complex state vector simulator.

pub struct QubitStateVector {
    num_qubits: usize,
    amplitudes: Vec<(f64, f64)>, // (Real, Imaginary)
}

impl QubitStateVector {
    pub fn new(num_qubits: usize) -> Self {
        let size = 1 << num_qubits;
        let mut amplitudes = vec![(0.0, 0.0); size];
        amplitudes[0] = (1.0, 0.0); // Initialize in |0...0> state
        
        Self {
            num_qubits,
            amplitudes,
        }
    }

    pub fn apply_hadamard(&mut self, target_qubit: usize) -> Result<(), &'static str> {
        if target_qubit >= self.num_qubits {
            return Err("Target qubit out of range");
        }

        let size = 1 << self.num_qubits;
        let inv_sqrt2 = 1.0 / 2.0_f64.sqrt();
        let step = 1 << target_qubit;

        // Zero-mock: applying H gate to the state vector
        for i in (0..size).step_by(step * 2) {
            for j in 0..step {
                let state0 = i + j;
                let state1 = i + j + step;
                
                let (r0, i0) = self.amplitudes[state0];
                let (r1, i1) = self.amplitudes[state1];

                self.amplitudes[state0] = ((r0 + r1) * inv_sqrt2, (i0 + i1) * inv_sqrt2);
                self.amplitudes[state1] = ((r0 - r1) * inv_sqrt2, (i0 - i1) * inv_sqrt2);
            }
        }

        Ok(())
    }
}
