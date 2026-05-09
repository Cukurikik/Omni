"""OMNI Security — LLM Agentic Confidentiality Manager"""
import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger("omni.llm_confidentiality")

class ConfidentialityPolicy:
    def __init__(self, allowed_domains: List[str], blocked_entities: List[str]):
        self.allowed_domains = allowed_domains
        self.blocked_entities = blocked_entities

class LLMConfidentialityManager:
    """
    Whispers in the Machine: Confidentiality in Agentic Systems.
    Intercepts and sanitizes LLM inputs/outputs to prevent data leakage 
    in multi-agent workflows.
    """
    def __init__(self, policy: ConfidentialityPolicy):
        self.policy = policy
        # Regex for generic PII detection
        self.pii_patterns = {
            "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "PHONE": r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',
            "SSN": r'\b\d{3}-\d{2}-\d{4}\b',
            "CREDIT_CARD": r'\b(?:\d[ -]*?){13,16}\b'
        }
        logger.info("Initialized Agentic Confidentiality Manager")

    def _redact_pii(self, text: str) -> Tuple[str, Dict[str, int]]:
        """Redacts PII and returns the sanitized text + stats."""
        sanitized = text
        stats = {k: 0 for k in self.pii_patterns.keys()}
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, sanitized)
            if matches:
                stats[pii_type] = len(matches)
                sanitized = re.sub(pattern, f"[{pii_type}_REDACTED]", sanitized)
                
        return sanitized, stats

    def enforce_prompt_confidentiality(self, prompt: str) -> str:
        """Sanitize prompt before sending to an external LLM agent."""
        sanitized, stats = self._redact_pii(prompt)
        
        # Enforce entity blocking
        for entity in self.policy.blocked_entities:
            # Case insensitive replace
            sanitized = re.sub(f(r'\b{entity}\b'), "[RESTRICTED_ENTITY]", sanitized, flags=re.IGNORECASE)
            
        logger.debug(f"Prompt sanitized. Redactions: {stats}")
        return sanitized

    def validate_agent_output(self, response: str) -> bool:
        """
        Check if the agent output violates confidentiality by revealing
        things it shouldn't, or hallucinating PII.
        """
        _, stats = self._redact_pii(response)
        
        # If the LLM generates PII that looks real, flag it
        total_violations = sum(stats.values())
        if total_violations > 0:
            logger.warning(f"Agent output blocked. Contained {total_violations} PII patterns.")
            return False
            
        # Check domain restrictions (e.g., URL generation)
        urls = re.findall(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', response)
        for url in urls:
            is_allowed = any(domain in url for domain in self.policy.allowed_domains)
            if not is_allowed:
                logger.warning(f"Agent output blocked. Unapproved domain: {url}")
                return False
                
        return True
