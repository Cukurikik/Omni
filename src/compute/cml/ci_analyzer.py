from typing import List, Dict, Tuple, Optional
import json

# OMNI CML: CI/CD Metric Analyzer
# Evaluates metric deltas between ML model commits for continuous integration gating.
# Source: iterative/cml

class CMLError(Exception):
    pass

def analyze_metric_delta(base_metrics: str, head_metrics: str, threshold: float = 0.05) -> Tuple[Optional[Dict[str, str]], Optional[CMLError]]:
    """
    Compares two JSON strings containing model metrics (e.g. {'accuracy': 0.9}).
    Returns a markdown report dictionary and/or an error.
    """
    try:
        base = json.loads(base_metrics)
        head = json.loads(head_metrics)
        
        report = []
        report.append("## Model Metrics Delta Report")
        report.append("| Metric | Base | Head | Delta | Status |")
        report.append("|---|---|---|---|---|")
        
        failed_checks = 0
        
        for key in head.keys():
            if key in base:
                val_base = float(base[key])
                val_head = float(head[key])
                delta = val_head - val_base
                
                # Assuming higher is better for all metrics for this simplified logic
                if delta < -threshold:
                    status = "🔴 Regression"
                    failed_checks += 1
                elif delta > threshold:
                    status = "🟢 Improvement"
                else:
                    status = "⚪ Stable"
                    
                report.append(f"| {key} | {val_base:.4f} | {val_head:.4f} | {delta:+.4f} | {status} |")
            else:
                report.append(f"| {key} | N/A | {float(head[key]):.4f} | N/A | 🆕 New |")
                
        report_str = "\n".join(report)
        
        if failed_checks > 0:
            report_str += f"\n\n**Warning**: {failed_checks} metrics regressed beyond the {threshold} threshold."
            
        return {"markdown": report_str, "pass": "true" if failed_checks == 0 else "false"}, None
        
    except json.JSONDecodeError:
        return None, CMLError("Invalid JSON format for metrics.")
    except ValueError as e:
        return None, CMLError(f"Invalid metric value (must be float): {str(e)}")
    except Exception as e:
        return None, CMLError(f"Analysis failed: {str(e)}")
