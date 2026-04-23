"""OmniShellLexerEngine for deterministic shell string tokenization."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniShellLexerEngine(OmniBaseEngine):
    """Production-grade Omni Shell Lexer Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def tokenize(self, command: str) -> Result[Dict[str, Any], str]:
        """
        Tokenizes a shell string, respecting single and double quotes.
        """
        try:
            if not isinstance(command, str):
                return Result.fail("Command must be a string")

            tokens = []
            current_token = []
            in_single = False
            in_double = False
            escape_next = False
            
            for char in command:
                if escape_next:
                    current_token.append(char)
                    escape_next = False
                elif char == '\\' and not in_single:
                    escape_next = True
                elif char == "'" and not in_double:
                    in_single = not in_single
                elif char == '"' and not in_single:
                    in_double = not in_double
                elif char.isspace() and not in_single and not in_double:
                    if current_token:
                        tokens.append("".join(current_token))
                        current_token = []
                elif char in ('|', '>', '<') and not in_single and not in_double:
                    if current_token:
                        tokens.append("".join(current_token))
                        current_token = []
                    tokens.append(char)
                else:
                    current_token.append(char)
                    
            if current_token:
                tokens.append("".join(current_token))

            if in_single or in_double:
                return Result.fail("Unclosed quote detected in command")

            return Result.ok({
                "tokens": tokens,
                "token_count": len(tokens)
            })
        except Exception as e:
            return Result.fail(str(e))

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniShellLexerEngine",
            "status": "operational",
            "complexity": "O(N)"
        }
