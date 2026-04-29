# Data Prep Kit Cleaner
from typing import Optional, Generic, TypeVar, List
import re

T = TypeVar('T'); E = TypeVar('E')
class OmniResult(Generic[T, E]):
    def __init__(self, value: Optional[T] = None, error: Optional[E] = None):
        self.is_ok = error is None; self.value = value; self.error = error

class TextCleaner:
    def clean_document(self, text: str, remove_urls: bool = True) -> OmniResult[str, str]:
        if text is None: return OmniResult(error="Text is none")
        
        cleaned = text
        if remove_urls:
            cleaned = re.sub(r'http[s]?://\S+', '', cleaned)
            
        # Remove repeated whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        # Remove non-ascii
        cleaned = cleaned.encode("ascii", "ignore").decode()
        
        return OmniResult(value=cleaned)
