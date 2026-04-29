// OMNI XGBoost Tree Split Engine — Compute Layer (Python)
// Absorbing dmlc/xgboost decision tree induction optimization
// Exact Gradient and Hessian node splitting algorithm.

from typing import List, Dict, Any, Tuple

class XGBError(Exception):
    pass

class NodeSplitInsight:
    def __init__(self, gain: float, threshold: float, left_weight: float, right_weight: float):
        self.gain = gain
        self.threshold = threshold
        self.left_weight = left_weight
        self.right_weight = right_weight

class OmniXgboostTreeSplit:
    def __init__(self, min_child_weight: float = 1.0, reg_lambda: float = 1.0):
        self.min_child_weight = min_child_weight
        self.reg_lambda = reg_lambda
        self.trees_evaluated = 0

    def compute_optimal_split(
        self,
        gh_pairs: List[Tuple[float, float]], # List of (Gradient, Hessian)
        feature_values: List[float]
    ) -> Tuple[bool, NodeSplitInsight, str]:
        """
        Determines the exact algebraic maximum gain threshold for a continuous feature line.
        """
        try:
            if not gh_pairs or not feature_values or len(gh_pairs) != len(feature_values):
                raise XGBError("Unbalanced instance vectors.")

            self.trees_evaluated += 1

            # 1. Sort instances by feature value
            instances = list(zip(feature_values, gh_pairs))
            instances.sort(key=lambda x: x[0])

            G_total = sum(g for _, (g, _) in instances)
            H_total = sum(h for _, (_, h) in instances)

            best_gain = -1.0
            best_threshold = 0.0
            best_left_weight = 0.0
            best_right_weight = 0.0

            G_L = 0.0
            H_L = 0.0

            # Linear scan over possible split points
            for i in range(len(instances) - 1):
                val, (g, h) = instances[i]
                
                G_L += g
                H_L += h
                
                G_R = G_total - G_L
                H_R = H_total - H_L

                # Enforce min child weight constraints
                if H_L < self.min_child_weight or H_R < self.min_child_weight:
                    continue

                # Identical feature values shouldn't split
                if val == instances[i+1][0]:
                    continue

                # Calculate similarity scores
                score_L = (G_L * G_L) / (H_L + self.reg_lambda)
                score_R = (G_R * G_R) / (H_R + self.reg_lambda)
                score_P = (G_total * G_total) / (H_total + self.reg_lambda)

                gain = 0.5 * (score_L + score_R - score_P)

                if gain > best_gain:
                    best_gain = gain
                    best_threshold = (val + instances[i+1][0]) / 2.0
                    best_left_weight = -G_L / (H_L + self.reg_lambda)
                    best_right_weight = -G_R / (H_R + self.reg_lambda)

            if best_gain < 0:
                # No valid split found
                return True, NodeSplitInsight(0.0, 0.0, 0.0, 0.0), ""

            return True, NodeSplitInsight(best_gain, best_threshold, best_left_weight, best_right_weight), ""

        except XGBError as e:
            return False, NodeSplitInsight(0.0,0.0,0.0,0.0), str(e)
        except Exception as e:
            return False, NodeSplitInsight(0.0,0.0,0.0,0.0), f"System panic: {e}"

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniXgboostTreeSplit",
            "feature_searches": self.trees_evaluated,
            "status": "Operational"
        }
