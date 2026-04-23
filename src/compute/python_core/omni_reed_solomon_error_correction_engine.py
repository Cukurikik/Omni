"""OmniReedSolomonErrorCorrectionEngine for error correction encoding."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniReedSolomonErrorCorrectionEngine(OmniBaseEngine):
    """Production-grade Omni Reed Solomon Error Correction Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def __init__(self):
        self.gf_exp = [0] * 512
        self.gf_log = [0] * 256
        x = 1
        for i in range(255):
            self.gf_exp[i] = x
            self.gf_log[x] = i
            x <<= 1
            if x & 0x100:
                x ^= 0x11D # Binary polynomial x^8 + x^4 + x^3 + x^2 + 1
        for i in range(255, 512):
            self.gf_exp[i] = self.gf_exp[i - 255]

    def _gf_mul(self, x: int, y: int) -> int:
        if x == 0 or y == 0:
            return 0
        return self.gf_exp[self.gf_log[x] + self.gf_log[y]]

    def _gf_poly_mul(self, p: List[int], q: List[int]) -> List[int]:
        r = [0] * (len(p) + len(q) - 1)
        for j in range(len(q)):
            for i in range(len(p)):
                r[i + j] ^= self._gf_mul(p[i], q[j])
        return r

    def _generator_poly(self, nsym: int) -> List[int]:
        g = [1]
        for i in range(nsym):
            g = self._gf_poly_mul(g, [1, self.gf_exp[i]])
        return g

    def encode(self, msg: bytes, nsym: int) -> Result[Dict[str, Any], str]:
        """Encodes an array of bytes using Reed-Solomon."""
        try:
            if nsym <= 0 or nsym >= 255:
                return Result.fail("Invalid number of symbols")
            gen = self._generator_poly(nsym)
            msg_out = list(msg) + [0] * nsym
            msg_list = list(msg)
            
            for i in range(len(msg_list)):
                coef = msg_out[i]
                if coef != 0:
                    for j in range(1, len(gen)):
                        msg_out[i + j] ^= self._gf_mul(gen[j], coef)
            
            parity = msg_out[len(msg_list):]
            return Result.ok({
                "message": list(msg),
                "parity": parity,
                "encoded": list(msg) + parity
            })
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniReedSolomonErrorCorrectionEngine",
            "status": "operational",
            "field": "GF(2^8)"
        }
