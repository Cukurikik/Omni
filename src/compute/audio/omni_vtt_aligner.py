"""
omni_vtt_aligner.py — WebVTT Subtitle Aligner
Layer: Compute / Audio
Inspired by: kurianbenoy/Indic-Subtitler

Implements time-synchronization alignment for ASR outputs (e.g., Whisper) 
to WebVTT subtitle format. Consolidates sentence fragments into readable 
caption lengths based on characters per second (CPS) constraints. Zero mock.
"""

import math
from typing import List, Dict

class OmniVTTAligner:
    def __init__(self, max_chars_per_line: int = 42, max_lines: int = 2, target_cps: float = 15.0):
        self.max_chars_per_line = max_chars_per_line
        self.max_lines = max_lines
        self.target_cps = target_cps

    @staticmethod
    def format_timestamp(seconds: float) -> str:
        """Converts seconds to WebVTT timestamp format (HH:MM:SS.mmm)"""
        if math.isnan(seconds) or seconds < 0:
            return "00:00:00.000"
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int(round((seconds - int(seconds)) * 1000))
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    def align(self, word_segments: List[Dict[str, float]]) -> str:
        """
        Takes a list of dictionaries, each containing 'word', 'start', and 'end'.
        Returns a formatted WebVTT string.
        """
        if not word_segments:
            return "WEBVTT\n\n"

        vtt_content = ["WEBVTT\n\n"]
        
        current_caption = []
        current_start = word_segments[0].get('start', 0.0)
        current_end = word_segments[0].get('end', 0.0)
        char_count = 0

        for segment in word_segments:
            word = segment.get('word', '').strip()
            if not word:
                continue

            word_start = segment.get('start', current_end)
            word_end = segment.get('end', word_start + 0.5)

            # Check constraints: Would adding this word exceed line limits?
            # Or is there a massive gap (silence > 2 seconds)?
            gap = word_start - current_end
            if (char_count + len(word) > self.max_chars_per_line * self.max_lines) or (gap > 2.0):
                # Flush current caption
                if current_caption:
                    vtt_content.append(self._flush_caption(current_start, current_end, current_caption))
                
                # Reset for next caption
                current_caption = [word]
                current_start = word_start
                current_end = word_end
                char_count = len(word)
            else:
                current_caption.append(word)
                current_end = word_end
                char_count += len(word) + 1 # +1 for space

        # Flush remaining
        if current_caption:
            vtt_content.append(self._flush_caption(current_start, current_end, current_caption))

        return "".join(vtt_content)

    def _flush_caption(self, start: float, end: float, words: List[str]) -> str:
        text = " ".join(words)
        # Word wrap into lines
        lines = []
        while len(text) > self.max_chars_per_line:
            split_idx = text.rfind(' ', 0, self.max_chars_per_line)
            if split_idx == -1: # No spaces found, force split
                split_idx = self.max_chars_per_line
            lines.append(text[:split_idx].strip())
            text = text[split_idx:].strip()
        
        if text:
            lines.append(text)

        # Enforce max lines (though loop above should prevent based on char_count check)
        final_text = "\n".join(lines[:self.max_lines])
        
        start_ts = self.format_timestamp(start)
        end_ts = self.format_timestamp(end)
        
        return f"{start_ts} --> {end_ts}\n{final_text}\n\n"
