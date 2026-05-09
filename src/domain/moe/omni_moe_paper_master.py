import json

# OMNI MOTHER Production Zero-Mock Paper Master
# Converts raw MoE outputs (research drafts, math formulas, reasoning traces)
# into compliant Academic HTML/Markdown formats compatible with Word/LaTeX.

class AcademicPaperFormatter:
    def __init__(self, title: str, authors: list):
        self.title = title
        self.authors = authors
        self.sections = []
        self.citations = {}

    def add_section(self, heading: str, content: str):
        self.sections.append({"heading": heading, "content": content})

    def add_citation(self, citation_id: str, reference: str):
        self.citations[citation_id] = reference

    def generate_html(self) -> str:
        html = [
            "<!DOCTYPE html>",
            "<html><head><meta charset='utf-8'><style>",
            "body { font-family: 'Times New Roman', serif; max-width: 800px; margin: 0 auto; padding: 2em; line-height: 1.6; }",
            "h1 { text-align: center; }",
            ".authors { text-align: center; font-style: italic; margin-bottom: 2em; }",
            ".abstract { margin: 2em 4em; font-size: 0.9em; }",
            "</style></head><body>"
        ]
        
        # Title & Authors
        html.append(f"<h1>{self.title}</h1>")
        html.append(f"<div class='authors'>{', '.join(self.authors)}<br/>OMNI Cognitive Engine</div>")
        
        # Sections
        for sec in self.sections:
            # Simple bold formatting for headings
            html.append(f"<h2>{sec['heading']}</h2>")
            
            # Format paragraphs
            paragraphs = sec['content'].split('\n\n')
            for p in paragraphs:
                html.append(f"<p>{p.strip()}</p>")
                
        # References
        if self.citations:
            html.append("<h2>References</h2><ol>")
            for ref in self.citations.values():
                html.append(f"<li>{ref}</li>")
            html.append("</ol>")
            
        html.append("</body></html>")
        return "\n".join(html)

    def export(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.generate_html())
        print(f"OMNI SYSTEM: Academic Paper exported successfully to {filepath}")
