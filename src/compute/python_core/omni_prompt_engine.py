"""
OMNI Compute — Prompt Template Engine
Jinja2-compatible prompt management for LLM serving.
"""
import re, logging, hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional

logger = logging.getLogger("omni.prompt")

@dataclass
class PromptTemplate:
    name: str; template: str; version: str = "1.0"
    system_prompt: str = ""; variables: List[str] = field(default_factory=list)
    max_tokens: int = 4096; stop_sequences: List[str] = field(default_factory=list)
    def __post_init__(self):
        if not self.variables:
            self.variables = re.findall(r'\{\{(\w+)\}\}', self.template)
    @property
    def hash(self) -> str:
        return hashlib.md5(f"{self.name}:{self.version}:{self.template}".encode()).hexdigest()[:12]

class OmniPromptEngine:
    """Production prompt template engine with versioning and validation."""
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self.history: List[Dict] = []
    def register(self, template: PromptTemplate):
        self.templates[template.name] = template
        logger.info(f"Template registered: {template.name} v{template.version}")
    def render(self, name: str, variables: Dict[str, str]) -> str:
        tmpl = self.templates.get(name)
        if not tmpl: raise ValueError(f"Template '{name}' not found")
        missing = [v for v in tmpl.variables if v not in variables]
        if missing: raise ValueError(f"Missing variables: {missing}")
        result = tmpl.template
        for key, value in variables.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        if tmpl.system_prompt:
            result = f"<|system|>\n{tmpl.system_prompt}\n<|end|>\n{result}"
        self.history.append({"template": name, "variables": list(variables.keys()), "hash": tmpl.hash})
        return result
    def render_chat(self, name: str, messages: List[Dict[str, str]]) -> str:
        tmpl = self.templates.get(name)
        parts = []
        if tmpl and tmpl.system_prompt:
            parts.append(f"<|system|>\n{tmpl.system_prompt}\n<|end|>")
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            parts.append(f"<|{role}|>\n{content}\n<|end|>")
        parts.append("<|assistant|>")
        return "\n".join(parts)
    def list_templates(self) -> List[Dict]:
        return [{"name": t.name, "version": t.version, "vars": t.variables, "hash": t.hash}
                for t in self.templates.values()]

# Built-in templates
BUILTIN_TEMPLATES = [
    PromptTemplate("chat", "{{message}}", system_prompt="You are a helpful assistant."),
    PromptTemplate("code", "Write code for: {{task}}\nLanguage: {{language}}\n\n```{{language}}", 
                   system_prompt="You are an expert programmer.", stop_sequences=["```"]),
    PromptTemplate("summarize", "Summarize the following:\n\n{{text}}\n\nSummary:",
                   system_prompt="You are a concise summarizer."),
    PromptTemplate("rag", "Context:\n{{context}}\n\nQuestion: {{question}}\n\nAnswer:",
                   system_prompt="Answer based on the provided context only."),
    PromptTemplate("reasoning", "{{question}}\n\nLet me think step by step:",
                   system_prompt="You are a careful reasoning assistant. Think step by step."),
]
