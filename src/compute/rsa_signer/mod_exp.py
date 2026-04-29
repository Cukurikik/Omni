class OmniResult:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    @property
    def is_ok(self):
        return self.error is None

class RSAMath:
    def __init__(self):
        pass

    def compute_modular_exponentiation(self, message: int, exponent: int, modulus: int) -> OmniResult:
        if message < 0 or exponent < 0 or modulus <= 0:
            return OmniResult(error="Invalid RSA parameters")

        if message >= modulus:
            return OmniResult(error="Message must be strictly less than modulus")

        # Deterministic RSA core mathematics: c = m^e mod n (or m = c^d mod n)
        # Using built-in pow for efficient O(log e) square-and-multiply algorithm
        try:
            result = pow(message, exponent, modulus)
            return OmniResult(value=result)
        except Exception as e:
            return OmniResult(error=str(e))
