"""OMNI Compute — Rhyme Generation Engine"""
import logging, re
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger("omni.rhyme")

class PhoneticDictionary:
    """Manages phonetic pronunciations (e.g., CMU Dict) for rhyme checking."""
    def __init__(self):
        # Simplified production dictionary (word -> phonemes)
        self.pronunciations: Dict[str, List[List[str]]] = {
            "light": [["L", "AY1", "T"]],
            "night": [["N", "AY1", "T"]],
            "bright": [["B", "R", "AY1", "T"]],
            "time": [["T", "AY1", "M"]],
            "rhyme": [["R", "AY1", "M"]],
            "code": [["K", "OW1", "D"]],
            "mode": [["M", "OW1", "D"]]
        }
        
    def get_rhyming_part(self, word: str) -> Optional[List[str]]:
        word = word.lower().strip()
        prons = self.pronunciations.get(word)
        if not prons:
            return None
        # Extract the last stressed vowel and everything after it
        phonemes = prons[0]
        for i in range(len(phonemes)-1, -1, -1):
            if any(char.isdigit() for char in phonemes[i]): # Vowel with stress
                return phonemes[i:]
        return phonemes

    def check_rhyme(self, word1: str, word2: str) -> bool:
        part1 = self.get_rhyming_part(word1)
        part2 = self.get_rhyming_part(word2)
        if not part1 or not part2:
            # Fallback to suffix matching if not in dictionary
            return word1[-3:] == word2[-3:] and word1 != word2
        return part1 == part2 and word1.lower() != word2.lower()

class RhymeTransformer:
    """Transformer constraint wrapper for generating rhyming poetry."""
    def __init__(self, vocab: List[str]):
        self.vocab = vocab
        self.phonetics = PhoneticDictionary()
        logger.info(f"Initialized RhymeTransformer with vocab size {len(vocab)}")
        
    def _extract_last_word(self, text: str) -> str:
        words = re.findall(r'\b\w+\b', text)
        return words[-1] if words else ""

    def apply_rhyme_logit_bias(self, logits: List[float], target_rhyme_word: str, bias_value: float = 10.0) -> List[float]:
        """Apply positive bias to vocabulary tokens that rhyme with the target word."""
        adjusted_logits = list(logits)
        for i, token_word in enumerate(self.vocab):
            if self.phonetics.check_rhyme(token_word, target_rhyme_word):
                adjusted_logits[i] += bias_value
        return adjusted_logits

    def generate_rhyming_couplet(self, prompt: str, target_word: str) -> str:
        """Simulates LLM generation strictly constrained to rhyme with target_word."""
        # Simulated generation logic
        rhyme_candidates = [w for w in self.vocab if self.phonetics.check_rhyme(w, target_word)]
        
        if not rhyme_candidates:
            rhyme_candidates = [target_word] # Fallback
            
        selected_rhyme = rhyme_candidates[0]
        return f"{prompt} {selected_rhyme}"

class PoetryPipeline:
    def __init__(self):
        self.vocab = ["light", "night", "bright", "time", "rhyme", "code", "mode", "star", "far"]
        self.transformer = RhymeTransformer(self.vocab)
        
    def create_stanza(self, lines_prompts: List[str], rhyme_scheme: str = "AABB") -> List[str]:
        stanza = []
        rhyme_targets = {}
        
        for i, prompt in enumerate(lines_prompts):
            scheme_char = rhyme_scheme[i % len(rhyme_scheme)]
            
            if scheme_char not in rhyme_targets:
                # First line of this rhyme scheme, just append (simulated)
                stanza.append(prompt + " light") 
                rhyme_targets[scheme_char] = "light"
            else:
                # Must rhyme with the target
                target = rhyme_targets[scheme_char]
                line = self.transformer.generate_rhyming_couplet(prompt, target)
                stanza.append(line)
                
        return stanza
