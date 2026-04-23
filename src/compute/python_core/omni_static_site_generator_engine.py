"""OmniStaticSiteGeneratorEngine for assembling structured HTML from an AST."""
from typing import Dict, Any, List
from src.compute.python_core.omni_base_engine import OmniBaseEngine, Result

class OmniStaticSiteGeneratorEngine(OmniBaseEngine):
    """Production-grade Omni Static Site Generator Engine for the OMNI Framework.

        Provides deterministic, zero-mock computational methods
        with monadic Result[T, E] error handling.
        """
    def generate_html(self, ast: Dict[str, Any]) -> Result[str, str]:
        """
        Recursively converts a valid structural AST into an HTML string.
        AST nodes must have 'tag', optional 'attributes' dict, and optional 'children'.
        Text nodes have a 'text' field instead of tag.
        """
        try:
            html_output = self._process_node(ast)
            return Result.ok(html_output)
        except Exception as e:
            return Result.fail(str(e))

    def _process_node(self, node: Dict[str, Any]) -> str:
        if 'text' in node:
            return str(node['text']).replace('<', '&lt;').replace('>', '&gt;')
            
        tag = str(node.get('tag', 'div')).lower()
        attributes = node.get('attributes', {})
        children = node.get('children', [])
        
        attr_str = ""
        for k, v in sorted(attributes.items()):
            attr_str += f' {k}="{v}"'
            
        # Void elements that do not require closing tags
        void_elements = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}
        
        if tag in void_elements:
            return f"<{tag}{attr_str}>"
            
        inner_html = "".join(self._process_node(child) for child in children)
        return f"<{tag}{attr_str}>{inner_html}</{tag}>"

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": "OmniStaticSiteGeneratorEngine",
            "status": "operational"
        }
