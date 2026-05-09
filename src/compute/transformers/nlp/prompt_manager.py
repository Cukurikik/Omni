"""
OMNI Transformer — Prompt Engineering & Template Manager
Production prompt management for LLM applications.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    name: str
    template: str
    input_variables: List[str]
    description: str = ""

    def format(self, **kwargs) -> str:
        missing = [v for v in self.input_variables if v not in kwargs]
        if missing:
            raise ValueError(f"Missing variables: {missing}")
        return self.template.format(**kwargs)


class PromptManager:
    """Manage prompt templates for LLM applications."""
    def __init__(self):
        self._templates: Dict[str, PromptTemplate] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(PromptTemplate(
            name="qa",
            template="Answer the following question based on the context.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:",
            input_variables=["context", "question"],
            description="Question answering with context",
        ))
        self.register(PromptTemplate(
            name="summarize",
            template="Summarize the following text in a concise manner.\n\nText: {text}\n\nSummary:",
            input_variables=["text"],
            description="Text summarization",
        ))
        self.register(PromptTemplate(
            name="classify",
            template="Classify the following text into one of these categories: {categories}\n\nText: {text}\n\nCategory:",
            input_variables=["text", "categories"],
            description="Text classification",
        ))
        self.register(PromptTemplate(
            name="translate",
            template="Translate the following text from {source_lang} to {target_lang}.\n\nText: {text}\n\nTranslation:",
            input_variables=["text", "source_lang", "target_lang"],
            description="Language translation",
        ))
        self.register(PromptTemplate(
            name="code_gen",
            template="Write {language} code for the following task.\n\nTask: {task}\n\nCode:\n```{language}",
            input_variables=["language", "task"],
            description="Code generation",
        ))
        self.register(PromptTemplate(
            name="chain_of_thought",
            template="Think step by step to solve this problem.\n\nProblem: {problem}\n\nStep-by-step solution:",
            input_variables=["problem"],
            description="Chain of thought reasoning",
        ))

    def register(self, template: PromptTemplate) -> None:
        self._templates[template.name] = template

    def get(self, name: str) -> PromptTemplate:
        if name not in self._templates:
            raise KeyError(f"Template '{name}' not found. Available: {list(self._templates.keys())}")
        return self._templates[name]

    def format(self, name: str, **kwargs) -> str:
        return self.get(name).format(**kwargs)

    def list_templates(self) -> List[str]:
        return list(self._templates.keys())

    def save(self, path: str) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        data = {name: {"template": t.template, "input_variables": t.input_variables, "description": t.description}
                for name, t in self._templates.items()}
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self, path: str) -> None:
        with open(path) as f:
            data = json.load(f)
        for name, info in data.items():
            self.register(PromptTemplate(name=name, **info))
