"""OmniHtmlParserEngine for parsing a subset of HTML."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniHtmlParserEngine(OmniBaseEngine):
    """Production-grade Omni Html Parser Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def parse(self, html: str) -> Result[Dict[str, Any], str]:
        """Parses a subset of HTML into a generic DOM tree representation."""
        try:
            self.pos = 0
            self.input = html
            nodes = self._parse_nodes()
            return Result.ok({"dom": nodes})
        except Exception as e:
            return Result.fail(str(e))

    def _parse_nodes(self) -> List[Dict[str, Any]]:
        nodes = []
        while True:
            self._consume_whitespace()
            if self.pos >= len(self.input):
                break
            if self.input[self.pos:self.pos+2] == "</":
                break
            if self.input[self.pos] == "<":
                nodes.append(self._parse_element())
            else:
                nodes.append(self._parse_text())
        return nodes

    def _parse_element(self) -> Dict[str, Any]:
        self._consume_char() # '<'
        tag_name = self._parse_tag_name()
        attrs = self._parse_attributes()
        
        # Self-closing check
        if self.input[self.pos:self.pos+2] == "/>":
            self._consume_char()
            self._consume_char()
            return {"type": "element", "tag": tag_name, "attributes": attrs, "children": []}
            
        self._consume_char() # '>'
        
        children = self._parse_nodes()
        
        # Expect closing tag
        if self.pos < len(self.input) and self.input[self.pos:self.pos+2] == "</":
            self._consume_char()
            self._consume_char()
            closing_tag = self._parse_tag_name()
            if tag_name != closing_tag:
                raise ValueError(f"Mismatched tags: expected {tag_name}, got {closing_tag}")
            self._consume_char() # '>'
            
        return {"type": "element", "tag": tag_name, "attributes": attrs, "children": children}

    def _parse_text(self) -> Dict[str, Any]:
        text = ""
        while self.pos < len(self.input) and self.input[self.pos] != "<":
            text += self._consume_char()
        return {"type": "text", "content": text.strip()}

    def _parse_tag_name(self) -> str:
        name = ""
        while self.pos < len(self.input) and self.input[self.pos].isalnum():
            name += self._consume_char()
        return name

    def _parse_attributes(self) -> Dict[str, str]:
        attrs = {}
        while True:
            self._consume_whitespace()
            if self.pos >= len(self.input) or self.input[self.pos] in [">", "/"]:
                break
            name = self._parse_tag_name()
            if self.input[self.pos] == "=":
                self._consume_char()
                quote = self._consume_char()
                val = ""
                while self.pos < len(self.input) and self.input[self.pos] != quote:
                    val += self._consume_char()
                self._consume_char()
                attrs[name] = val
            elif name:
                attrs[name] = ""
        return attrs

    def _consume_char(self) -> str:
        ch = self.input[self.pos]
        self.pos += 1
        return ch

    def _consume_whitespace(self):
        while self.pos < len(self.input) and self.input[self.pos].isspace():
            self.pos += 1

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniHtmlParserEngine",
            "status": "operational",
            "parser_type": "recursive_descent"
        }
