"""
moe_anime_quiz_expert.py — Domain / Core
Layer: Domain / AI — Anime Quiz Domain Expert

Inspired by `przemub/anime_quiz`. 
In an MoE architecture, Expert #12 is explicitly trained on anime themes,
myanimelist data, and visual novel scripts. This module acts as the domain 
interface, verifying answers against the LLM's generated tokens for the quiz app.
"""

import json
from typing import Dict, List

class AnimeQuizExpert:
    def __init__(self):
        # A mock database of valid anime openings/themes
        self.theme_database: Dict[str, List[str]] = {
            "Cruel Angel's Thesis": ["Neon Genesis Evangelion", "Evangelion", "NGE"],
            "Unravel": ["Tokyo Ghoul", "TG"],
            "Guren no Yumiya": ["Attack on Titan", "Shingeki no Kyojin", "AoT", "SnK"]
        }
        print("[Anime Quiz] Initialized Domain Expert #12 (Anime/Manga DB).")

    def evaluate_llm_response(self, user_guess: str, actual_song: str) -> bool:
        """
        Validates if the user's guess (or the LLM's parsed answer) matches the 
        accepted aliases for the anime theme.
        """
        valid_answers = self.theme_database.get(actual_song, [])
        if not valid_answers:
            print(f"[Anime Quiz] Warning: Song '{actual_song}' not found in DB.")
            return False
            
        guess_clean = user_guess.strip().lower()
        
        for valid in valid_answers:
            if guess_clean == valid.lower():
                return True
                
        return False

    def generate_quiz_prompt(self, song_name: str) -> str:
        """
        Constructs a highly structured prompt to force the MoE to act as a quiz master.
        """
        return f"""
        [SYSTEM: You are the Anime Theme Quiz Master. Be energetic and use Moe vocabulary.]
        [TASK] The current song playing is '{song_name}'. Give the user a tiny, cryptic hint 
        about the anime this belongs to, without revealing the title.
        [CONSTRAINTS] Maximum 2 sentences. Use emotes like (๑• ω •๑).
        """
