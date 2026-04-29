# OMNI MOTHER - DIVINE MEMORY INTEGRATION
# Awesome NLP Preprocessor (OMNI Zero-Mock Implementation)
# Implements standard regex-based text normalization pipelines.

from dataclasses import dataclass
from typing import List, Optional
import re

@dataclass
class Result:
    value: Optional[str]
    error: Optional[str]
    is_ok: bool

    @staticmethod
    def ok(val: str) -> 'Result':
        return Result(value=val, error=None, is_ok=True)

    @staticmethod
    def err(err: str) -> 'Result':
        return Result(value=None, error=err, is_ok=False)

class NLPPreprocessor:
    def __init__(self, remove_urls: bool = True, lowercase: bool = True):
        self.remove_urls = remove_urls
        self.lowercase = lowercase
        
        # Precompile exact matched regexes (production standard)
        self.url_regex = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
        self.punct_regex = re.compile(r'[^\w\s]')

    def clean_text(self, text: str) -> Result:
        if not text:
            return Result.err("Input string is empty.")
            
        processed = text
        
        if self.remove_urls:
            processed = self.url_regex.sub('', processed)
            
        # Strip trailing/leading spaces
        processed = processed.strip()
        
        # Remove multiple spaces
        processed = re.sub(r'\s+', ' ', processed)
        
        if self.lowercase:
            processed = processed.lower()
            
        return Result.ok(processed)
