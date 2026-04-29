# Omni Awesome Chinese LLM Evaluator
# Ref: zhenlohuang/awesome-chinese-llm
import re
from typing import List, Dict

def tokenize_chinese_chars(text: str) -> List[str]:
    # Extract only CJK characters
    cjk_pattern = re.compile(r'[\u4e00-\u9fff]')
    return cjk_pattern.findall(text)

def chinese_bleu_approximation(prediction: str, reference: str) -> float:
    pred_chars = tokenize_chinese_chars(prediction)
    ref_chars = tokenize_chinese_chars(reference)
    
    if not pred_chars or not ref_chars:
        return 0.0
        
    pred_ngrams = [tuple(pred_chars[i:i+2]) for i in range(len(pred_chars)-1)]
    ref_ngrams = [tuple(ref_chars[i:i+2]) for i in range(len(ref_chars)-1)]
    
    if not pred_ngrams or not ref_ngrams:
        return 0.0
        
    overlap = len(set(pred_ngrams) & set(ref_ngrams))
    precision = overlap / len(pred_ngrams)
    
    # Brevity penalty
    bp = 1.0 if len(pred_chars) > len(ref_chars) else 2.718 ** (1 - len(ref_chars)/len(pred_chars))
    return round(bp * precision, 4)

def chinese_dataset_stats(texts: List[str]) -> Dict[str, float]:
    total_chars = sum(len(tokenize_chinese_chars(t)) for t in texts)
    avg_len = total_chars / max(len(texts), 1)
    return {
        "n_samples": float(len(texts)),
        "total_cjk_chars": float(total_chars),
        "avg_cjk_len": round(avg_len, 2)
    }
