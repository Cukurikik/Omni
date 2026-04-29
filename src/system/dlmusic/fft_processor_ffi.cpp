// OMNI SYSTEM LAYER: DL Music (C++)
// Fast Fourier Transform (FFT) acceleration using pure C++ math.

#include <complex>
#include <vector>
#include <cmath>

extern "C" {

    const double PI = 3.141592653589793238460;
    typedef std::complex<double> Complex;

    // Cooley-Tukey Radix-2 FFT
    void fft_compute(std::vector<Complex>& a) {
        int n = a.size();
        if (n <= 1) return;

        std::vector<Complex> even(n / 2), odd(n / 2);
        for (int i = 0; i < n / 2; i++) {
            even[i] = a[i * 2];
            odd[i] = a[i * 2 + 1];
        }

        fft_compute(even);
        fft_compute(odd);

        for (int i = 0; i < n / 2; i++) {
            Complex t = std::polar(1.0, -2 * PI * i / n) * odd[i];
            a[i] = even[i] + t;
            a[i + n / 2] = even[i] - t;
        }
    }

    int omni_run_fft(double* real_in, double* imag_out, int length) {
        if (!real_in || !imag_out || length <= 0 || (length & (length - 1)) != 0) {
            return -1; // Must be power of 2
        }

        std::vector<Complex> a(length);
        for (int i = 0; i < length; i++) {
            a[i] = Complex(real_in[i], 0);
        }

        fft_compute(a);

        for (int i = 0; i < length; i++) {
            imag_out[i] = std::abs(a[i]); // Returning magnitude
        }

        return 0; // Success
    }

}
