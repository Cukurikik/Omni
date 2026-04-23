"""
OMNI Financial Taxation Rule Engine.
Assimilated from: gabrieldim/Accounting-System-Software-Testing (Level 2 Abstraction)
Provides: Progressive hierarchical calculation bracket for deterministic accounting extraction rates.
"""
from typing import Any, List, Dict
from src.compute.python_core.omni_base_engine import Result, Ok, Err

ENGINE_VERSION = "2.0.0-omni-financial-taxation-rule"




class OmniFinancialTaxationRuleEngine:
    """
    Evaluates net-worth liability using progressive multi-layered percentage chunking logic.
    
    @since 2.0.0
    @tags ["accounting", "taxation", "testing", "finance"]
    """
    def __init__(self) -> None:
        self._omni_version: str = "3.0.0-OMNI-NEXUS"

        # Tier structure: (Max_Limit_for_Tier, Rate)
        self._tax_tiers = [
            (10000.0, 0.0),    # 0 to 10k: 0%
            (40000.0, 0.10),   # 10k to 50k: 10%
            (100000.0, 0.20),  # 50k to 150k: 20%
            (float('inf'), 0.35) # > 150k: 35%
        ]

    def diagnostics(self) -> Result:
        res = self.calculate_progressive_liability(10000.0)
        if res.is_ok() and res.value["total_liability"] == 0.0:
            return Ok({"engine": "FinancialTaxationRule", "status": "Ready", "tax_tiers": "Functional"})
        return Err("Progressive tier structure breached determinism.")

    def calculate_progressive_liability(self, gross_income: float) -> Result:
        """
        Reduces gross string via successive bracket chunking (Mathematical Tier Separation).
        """
        if gross_income < 0.0:
            return Err("Income vector cannot drop below absolute zero in standard taxation logic.")

        remaining = gross_income
        total_tax = 0.0
        liability_breakdown = []

        for limit, rate in self._tax_tiers:
            if remaining <= 0:
                break
                
            chunk = min(remaining, limit)
            tax_for_chunk = chunk * rate
            
            total_tax += tax_for_chunk
            remaining -= chunk
            
            liability_breakdown.append({
                "chunk_taxed": chunk,
                "rate_applied": rate,
                "tax_yield": tax_for_chunk
            })

        net = gross_income - total_tax

        return Ok({
            "gross_input": gross_income,
            "total_liability": total_tax,
            "net_output": net,
            "effective_tax_rate": (total_tax / gross_income) if gross_income > 0 else 0.0,
            "breakdown": liability_breakdown
        })
