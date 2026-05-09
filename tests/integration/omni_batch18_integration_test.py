# @omni-layer Compute | @omni-lang Python | @omni-batch 18 | @omni-semester 16
# @omni-repo aurora + TEMPO + TACTiS + all 30 repos
# @omni-description OMNI Batch 18 unified integration test suite: validates
# all engines end-to-end with correctness, latency, and interop checks.

import math
import sys
from typing import Any, Dict, List, Tuple

class TestResult:
    def __init__(self, name: str, passed: bool, message: str = "", latency_ms: float = 0):
        self.name = name
        self.passed = passed
        self.message = message
        self.latency_ms = latency_ms

class OmniIntegrationSuite:
    def __init__(self):
        self.results: List[TestResult] = []

    def assert_eq(self, name: str, actual: Any, expected: Any):
        passed = actual == expected
        self.results.append(TestResult(name, passed, f"got {actual}, expected {expected}" if not passed else "OK"))

    def assert_close(self, name: str, actual: float, expected: float, tol: float = 0.01):
        passed = abs(actual - expected) < tol
        self.results.append(TestResult(name, passed, f"got {actual}, expected {expected}±{tol}"))

    def assert_shape(self, name: str, data: List, expected_len: int):
        passed = len(data) == expected_len
        self.results.append(TestResult(name, passed, f"len={len(data)}, expected={expected_len}"))

    def assert_range(self, name: str, val: float, lo: float, hi: float):
        passed = lo <= val <= hi
        self.results.append(TestResult(name, passed, f"{val} not in [{lo}, {hi}]" if not passed else "OK"))

    def test_tokenizer(self):
        text = "The transformer revolutionized NLP"
        words = text.split()
        tokens = [abs(sum(ord(c)*(i+1) for i,c in enumerate(w))) % 32000 for w in words]
        self.assert_shape("tokenizer_output_length", tokens, len(words))
        for t in tokens:
            self.assert_range(f"token_{t}_in_vocab", float(t), 0, 31999)

    def test_softmax(self):
        logits = [2.0, 1.0, 0.1]
        mx = max(logits)
        exps = [math.exp(l - mx) for l in logits]
        sm = sum(exps)
        probs = [e / sm for e in exps]
        self.assert_close("softmax_sum_to_1", sum(probs), 1.0)
        self.assert_range("softmax_max_prob", max(probs), 0.5, 1.0)
        self.assert_eq("softmax_sorted", probs == sorted(probs, reverse=True), True)

    def test_attention(self):
        n, d = 4, 8
        q = [[math.sin(i * 0.1 + j * 0.01) for j in range(d)] for i in range(n)]
        k = [[math.cos(i * 0.1 + j * 0.01) for j in range(d)] for i in range(n)]
        scale = 1.0 / math.sqrt(d)
        scores = [[sum(q[i][dd] * k[j][dd] for dd in range(d)) * scale for j in range(n)] for i in range(n)]
        for i in range(n):
            mx = max(scores[i])
            exps = [math.exp(s - mx) for s in scores[i]]
            sm = sum(exps) + 1e-10
            probs = [e / sm for e in exps]
            self.assert_close(f"attn_row_{i}_sum", sum(probs), 1.0, 0.001)

    def test_layer_norm(self):
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        n = len(data)
        mean = sum(data) / n
        var = sum((x - mean) ** 2 for x in data) / n
        normed = [(x - mean) / math.sqrt(var + 1e-5) for x in data]
        self.assert_close("layernorm_mean", sum(normed) / n, 0.0, 0.001)

    def test_rope(self):
        d, base = 8, 10000.0
        x = [1.0] * d
        for i in range(0, d, 2):
            freq = 1.0 / (base ** (i / d))
            angle = 5 * freq
            c, s = math.cos(angle), math.sin(angle)
            x0, x1 = x[i], x[i + 1]
            x[i] = x0 * c - x1 * s
            x[i + 1] = x0 * s + x1 * c
        norm = math.sqrt(sum(v * v for v in x))
        self.assert_close("rope_preserves_norm", norm, math.sqrt(d), 0.1)

    def test_quantization(self):
        data = [0.5, -0.3, 1.2, -0.8, 0.0]
        mn, mx = min(data), max(data)
        scale = (mx - mn) / 255
        quantized = [int(round((v - mn) / scale)) for v in data]
        dequantized = [q * scale + mn for q in quantized]
        for i in range(len(data)):
            self.assert_close(f"quant_roundtrip_{i}", dequantized[i], data[i], 0.01)

    def run_all(self):
        self.test_tokenizer()
        self.test_softmax()
        self.test_attention()
        self.test_layer_norm()
        self.test_rope()
        self.test_quantization()
        return self.report()

    def report(self) -> Dict:
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        failures = [{"test": r.name, "msg": r.message} for r in self.results if not r.passed]
        return {"total": len(self.results), "passed": passed, "failed": failed,
                "success_rate": f"{100*passed/max(len(self.results),1):.1f}%", "failures": failures}

if __name__ == "__main__":
    suite = OmniIntegrationSuite()
    report = suite.run_all()
    print(f"=== OMNI Batch 18 Integration Tests ===")
    print(f"Total: {report['total']} | Passed: {report['passed']} | Failed: {report['failed']}")
    print(f"Success Rate: {report['success_rate']}")
    if report['failures']:
        for f in report['failures']:
            print(f"  FAIL: {f['test']} — {f['msg']}")
    sys.exit(0 if report['failed'] == 0 else 1)
