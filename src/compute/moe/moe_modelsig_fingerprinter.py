# moe_modelsig_fingerprinter.py — Compute Layer: Model Signature Fingerprinter
# Generates structural architectures fingerprints to compare LLMs without full weight loading.

import hashlib
from typing import Dict, Any

class ModelFingerprinter:
    @staticmethod
    def generate_fingerprint(config_json: Dict[str, Any]) -> str:
        """
        Extracts structural components (GQA, heads, hidden_size, moe_experts)
        and generates a deterministic SHA-256 fingerprint.
        """
        structural_keys = [
            "hidden_size", 
            "num_attention_heads", 
            "num_key_value_heads", 
            "num_hidden_layers",
            "vocab_size",
            "num_local_experts" # MoE specific
        ]
        
        signature_string = ""
        for key in sorted(structural_keys):
            val = config_json.get(key, 0)
            signature_string += f"{key}:{val}|"
            
        hash_object = hashlib.sha256(signature_string.encode('utf-8'))
        return hash_object.hexdigest()
        
    @staticmethod
    def identify_proxy_compatibility(fingerprint_a: str, fingerprint_b: str) -> bool:
        """
        Determines if Model B can act as a proxy test target for Model A in TensorRT-LLM.
        """
        return fingerprint_a == fingerprint_b
