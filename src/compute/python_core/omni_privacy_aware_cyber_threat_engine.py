from __future__ import annotations
from typing import Dict, Any, List
import math
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class OmniPrivacyAwareCyberThreatEngine:
    """
    omni-privacy-aware-cyber-threat
    
    Mathematical privacy-aware network anomaly identifier via standard divergence thresholds.
    Models Cybria's federated learning threat anomaly concepts natively using standard deviations.
    """
    
    ENGINE_VERSION = "omni-s11-b4.1.0"
    
    def __init__(self, deviation_threshold: float = 2.5) -> None:
        """Sets the Z-Score outlier threshold bounds."""
        self.deviation_threshold = deviation_threshold

    def evaluate_telemetry_variance(self, federated_packets: List[float]) -> Result:
        """
        Natively identifies outliers in a distribution of packet metrics mathematically.
        Zero dependencies on external ML frameworks.
        """
        try:
            if not federated_packets:
                return Err(ValueError("Empty telemetry bounds block provided."))
                
            n = len(federated_packets)
            if n < 3:
                return Err(ValueError("Insufficient sample bounds for statistical variance."))
                
            # Compute mean natively
            mean_val = sum(federated_packets) / n
            
            # Compute variance natively
            variance = sum((x - mean_val) ** 2 for x in federated_packets) / (n - 1)
            std_dev = math.sqrt(variance)
            
            if std_dev == 0.0:
                # Distribution is completely flat; no anomalies
                return Ok({"anomalies": [], "threat_level": 0.0, "safe_packets": n})
            
            anomalies = []
            for i, packet in enumerate(federated_packets):
                z_score = abs(packet - mean_val) / std_dev
                if z_score > self.deviation_threshold:
                    anomalies.append({"index": i, "value": packet, "z_score": round(z_score, 4)})
                    
            threat_level = round(len(anomalies) / n, 4)
            
            return Ok({
                "anomalies": anomalies,
                "threat_level": threat_level,
                "safe_packets": n - len(anomalies),
                "z_threshold": self.deviation_threshold
            })
            
        except Exception as e:
            return Err(e)

    def diagnostics(self) -> Dict[str, Any]:
        """OMNI Framework status."""
        return {
            "engine": "OmniPrivacyAwareCyberThreatEngine",
            "version": self.ENGINE_VERSION,
            "status": "operational",
            "threshold": self.deviation_threshold,
            "complexity": "O(N) Variance Map"
        }
