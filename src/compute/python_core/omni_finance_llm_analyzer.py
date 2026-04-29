import re

class OmniFinanceLLMAnalyzer:
    """OMNI Compute Layer: Finance LLMs Extraction Engine"""
    
    def __init__(self):
        self.ticker_pattern = re.compile(r'\$([A-Z]{1,5})')

    def extract_tickers(self, financial_text: str) -> list[str]:
        if not financial_text:
            return []
            
        # Deterministic regex extraction of tickers like $AAPL
        matches = self.ticker_pattern.findall(financial_text.upper())
        return list(set(matches))

    def evaluate_sentiment(self, text: str) -> str:
        text_lower = text.lower()
        bullish = ["up", "growth", "bull", "surge", "beat"]
        bearish = ["down", "drop", "bear", "miss", "crash"]
        
        bull_score = sum(1 for word in bullish if word in text_lower)
        bear_score = sum(1 for word in bearish if word in text_lower)
        
        if bull_score > bear_score: return "BULLISH"
        elif bear_score > bull_score: return "BEARISH"
        return "NEUTRAL"
