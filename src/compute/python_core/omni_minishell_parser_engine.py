"""OmniMinishellParserEngine for parsing shell commands into AST."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniMinishellParserEngine(OmniBaseEngine):
    """Production-grade Omni Minishell Parser Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def parse(self, command_line: str) -> Result[Dict[str, Any], str]:
        """Parses a command line into a list of piped commands with redirects."""
        try:
            tokens = self._tokenize(command_line)
            ast = self._build_ast(tokens)
            return Result.ok({"ast": ast})
        except Exception as e:
            return Result.fail(f"Parse error: {str(e)}")

    def _tokenize(self, line: str) -> List[str]:
        tokens = []
        curr = []
        in_sq = False
        in_dq = False
        i = 0
        while i < len(line):
            c = line[i]
            if c == "'" and not in_dq:
                in_sq = not in_sq
                curr.append(c)
            elif c == '"' and not in_sq:
                in_dq = not in_dq
                curr.append(c)
            elif c in ['|', '<', '>'] and not in_sq and not in_dq:
                if curr:
                    tokens.append(''.join(curr).strip())
                    curr = []
                if c == '>' and i + 1 < len(line) and line[i+1] == '>':
                    tokens.append('>>')
                    i += 1
                elif c == '<' and i + 1 < len(line) and line[i+1] == '<':
                    tokens.append('<<')
                    i += 1
                else:
                    tokens.append(c)
            elif c.isspace() and not in_sq and not in_dq:
                if curr:
                    tokens.append(''.join(curr).strip())
                    curr = []
            else:
                curr.append(c)
            i += 1
        if curr:
            tok = ''.join(curr).strip()
            if tok:
                tokens.append(tok)
        return [t for t in tokens if t]

    def _build_ast(self, tokens: List[str]) -> List[Dict[str, Any]]:
        ast = []
        curr_cmd = {"args": [], "redirects": []}
        i = 0
        while i < len(tokens):
            tok = tokens[i]
            if tok == '|':
                ast.append(curr_cmd)
                curr_cmd = {"args": [], "redirects": []}
            elif tok in ['<', '>', '>>', '<<']:
                if i + 1 < len(tokens):
                    curr_cmd["redirects"].append({"op": tok, "target": tokens[i+1]})
                    i += 1
                else:
                    raise ValueError(f"Syntax error near unexpected token {tok}")
            else:
                # Remove surrounding quotes if cleanly matched
                if (tok.startswith("'") and tok.endswith("'")) or (tok.startswith('"') and tok.endswith('"')):
                    if len(tok) >= 2:
                        tok = tok[1:-1]
                curr_cmd["args"].append(tok)
            i += 1
        if curr_cmd["args"] or curr_cmd["redirects"]:
            ast.append(curr_cmd)
        return ast

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniMinishellParserEngine",
            "status": "operational",
            "capabilities": ["tokenize", "ast_build", "redirection_parsing"]
        }
