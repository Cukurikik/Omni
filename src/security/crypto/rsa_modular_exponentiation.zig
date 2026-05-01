const std = @import("std");

/// OMNI MOTHER SYSTEM - SECURITY LAYER
/// RSA Modular Exponentiation
/// Mathematically evaluates large integer geometries using the "Square-and-Multiply" algorithm to compute (base^exp) mod N securely.
/// Absorbed from: OMNI Crypto Hardening

pub const RSAError = error{
    DivisionByZero,
    ModulusTooSmall,
};

pub const RSAModularMath = struct {

    /// Executes fast modular exponentiation.
    /// Evaluates: result = (base ^ exp) % modulus
    /// 
    /// Standard u64 computed limits the bit width, but the structural geometry of 
    /// Right-to-Left binary method applies to BigInt abstractions.
    pub fn modular_exponentiation(base: u64, exp: u64, modulus: u64) !u64 {
        if (modulus == 0) return RSAError.DivisionByZero;
        if (modulus == 1) return 0; // Everything mod 1 is 0

        var result: u128 = 1;
        var b: u128 = base % modulus;
        var e: u64 = exp;

        // Square-and-Multiply algorithm
        while (e > 0) {
            // If the current lowest bit of exponent is 1, multiply result by base
            if (e % 2 == 1) {
                result = (result * b) % modulus;
            }
            
            // Shift exponent right
            e >>= 1;

            // Square the base
            b = (b * b) % modulus;
        }

        return @as(u64, @truncate(result));
    }

    /// Evaluates a safe computed for RSA Encryption: C = (M^e) mod N
    /// N is the public modulus, e is the public exponent.
    pub fn encrypt(message: u64, public_exponent: u64, modulus: u64) !u64 {
        if (message >= modulus) return RSAError.ModulusTooSmall; // Message must be smaller than modulus
        return modular_exponentiation(message, public_exponent, modulus);
    }

    /// Evaluates a safe computed for RSA Decryption: M = (C^d) mod N
    /// N is the public modulus, d is the private exponent.
    pub fn decrypt(ciphertext: u64, private_exponent: u64, modulus: u64) !u64 {
        if (ciphertext >= modulus) return RSAError.ModulusTooSmall;
        return modular_exponentiation(ciphertext, private_exponent, modulus);
    }
};
