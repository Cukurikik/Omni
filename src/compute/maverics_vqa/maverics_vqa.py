import math

class MavericsVQAError(Exception):
    pass

class Result:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def unwrap(self):
        if not self.is_ok():
            raise self.error
        return self.value

# OMNI Engine: maverics-vqa
# Computes evaluation alignment based on manually-validated VQ-Square examples.
class MavericsBenchEngine:
    def __init__(self, validation_strictness: float = 0.9):
        self.strictness = validation_strictness

    def compute_bench_alignment(self, visual_iou: float, textual_bleu: float) -> Result:
        try:
            if visual_iou < 0.0 or visual_iou > 1.0 or textual_bleu < 0.0 or textual_bleu > 1.0:
                 return Result(error=MavericsVQAError("Evaluation metric limits outside of 0.0-1.0 geometry"))

            # Maverics requires high alignment between visual and textual evaluation scores
            alignment_score = math.sqrt(visual_iou * textual_bleu)

            if alignment_score < self.strictness:
                return Result(value={
                    "maverics_approved": False,
                    "alignment": alignment_score,
                    "reason": "VQA answers drifted past evaluated benchmark caps"
                })

            return Result(value={
                "maverics_approved": True,
                "alignment": alignment_score,
                "reason": "Strict benchmark alignment"
            })

        except Exception as e:
            return Result(error=MavericsVQAError(f"Maverics calculation failure: {str(e)}"))
