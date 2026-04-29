# Omni ChemLLMBench Chemistry Evaluation Engine
# Ref: ChemFoundationModels/ChemLLMBench — NeurIPS'23
from typing import List, Dict

def name_to_smiles_accuracy(preds: List[str], golds: List[str]) -> Dict:
    correct = sum(1 for p, g in zip(preds, golds) if p.strip() == g.strip())
    return {"accuracy": round(correct / max(len(golds), 1), 4), "n": len(golds)}

def property_prediction_mae(preds: List[float], golds: List[float]) -> Dict:
    if not golds: return {"mae": 0, "n": 0}
    mae = sum(abs(p-g) for p, g in zip(preds, golds)) / len(golds)
    return {"mae": round(mae, 4), "n": len(golds)}

def reaction_prediction_score(pred_products: List[str], gold_products: List[str]) -> Dict:
    exact = sum(1 for p, g in zip(pred_products, gold_products) if p.strip() == g.strip())
    return {"exact_match": round(exact / max(len(gold_products), 1), 4)}

def retrosynthesis_eval(pred_reactants: List[str], gold_reactants: List[str]) -> Dict:
    correct = sum(1 for p, g in zip(pred_reactants, gold_reactants) if set(p.split('.')) == set(g.split('.')))
    return {"top1_accuracy": round(correct / max(len(gold_reactants), 1), 4)}
