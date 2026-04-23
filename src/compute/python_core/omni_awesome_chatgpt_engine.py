"""
OMNI Awesome ChatGPT Engine
==============================
Production-grade OMNI engine abstracting a curated resource catalog
for ChatGPT/GPT ecosystem tools, SDKs, and integrations.
Inspired by eon01/awesome-chatgpt.

Features:
- Structured catalog of ChatGPT libraries, SDKs, and APIs by language.
- Resource search with category filtering and relevance ranking.
- Integration discovery (browser extensions, IDE plugins, bots).
- Prompt template library with parameter substitution.
- Monadic Result encapsulation preventing runtime trace crashes.

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad
# ---------------------------------------------------------------------------

ENGINE_VERSION = "1.0.0-omni"
from src.compute.python_core.omni_base_engine import Result, Ok, Err


class AwesomeChatGPTErr(Exception):
    """Base error for AwesomeChatGPT engine."""
    pass


@dataclass(frozen=True)
class Ok:
    """Monadic Ok result type."""
    value: Any


@dataclass(frozen=True)
class Err:
    """Monadic Err result type."""
    error: str


Result = Union[Ok, Err]


# ---------------------------------------------------------------------------
# 2. CATALOG DATA STRUCTURES
# ---------------------------------------------------------------------------

class ResourceCategory(Enum):
    """Category of a ChatGPT ecosystem resource."""
    SDK_PYTHON = "sdk-python"
    SDK_JAVASCRIPT = "sdk-javascript"
    SDK_GOLANG = "sdk-golang"
    SDK_RUST = "sdk-rust"
    SDK_TYPESCRIPT = "sdk-typescript"
    SDK_KOTLIN = "sdk-kotlin"
    SDK_SWIFT = "sdk-swift"
    SDK_PHP = "sdk-php"
    SDK_DOTNET = "sdk-dotnet"
    SDK_RUBY = "sdk-ruby"
    SDK_JAVA = "sdk-java"
    BROWSER_EXTENSION = "browser-extension"
    IDE_PLUGIN = "ide-plugin"
    CHATBOT = "chatbot"
    PROMPT_LIBRARY = "prompt-library"
    WEB_APP = "web-app"
    DESKTOP_APP = "desktop-app"
    RESEARCH_PAPER = "research-paper"
    TUTORIAL = "tutorial"
    EMBEDDING_DB = "embedding-db"
    AI_ASSISTANT = "ai-assistant"


@dataclass
class Resource:
    """A single resource entry in the catalog."""
    name: str
    url: str
    category: ResourceCategory
    description: str = ""
    tags: List[str] = field(default_factory=list)
    stars: int = 0
    language: str = ""


@dataclass
class PromptTemplate:
    """A reusable prompt template with parameter slots."""
    name: str
    template: str
    parameters: List[str] = field(default_factory=list)
    category: str = "general"


# ---------------------------------------------------------------------------
# 3. CATALOG ENGINE
# ---------------------------------------------------------------------------

class ResourceCatalog:
    """Manages the curated resource catalog."""

    def __init__(self) -> None:
        """Initialise with built-in seed data."""
        self._resources: List[Resource] = []
        self._seed_catalog()

    def _seed_catalog(self) -> None:
        """Populate with well-known ChatGPT resources."""
        seeds = [
            Resource("openai-python", "https://github.com/openai/openai-python",
                     ResourceCategory.SDK_PYTHON,
                     "Official OpenAI Python library", ["openai", "api"], 20000, "Python"),
            Resource("openai-node", "https://github.com/openai/openai-node",
                     ResourceCategory.SDK_JAVASCRIPT,
                     "Official OpenAI Node.js / TypeScript library", ["openai"], 7000, "JavaScript"),
            Resource("go-openai", "https://github.com/sashabaranov/go-openai",
                     ResourceCategory.SDK_GOLANG,
                     "OpenAI ChatGPT, GPT-3, GPT-4 API client for Go", ["gpt", "go"], 8000, "Go"),
            Resource("chatgpt-rs", "https://github.com/nicholasgasior/chatgpt-rs",
                     ResourceCategory.SDK_RUST,
                     "Rust client for OpenAI", ["rust"], 500, "Rust"),
            Resource("chatgpt-web", "https://github.com/Chanzhaoyu/chatgpt-web",
                     ResourceCategory.WEB_APP,
                     "ChatGPT Web application using Express and Vue3", ["web"], 30000),
            Resource("chatgpt-chrome-extension", "https://github.com/gragland/chatgpt-chrome-extension",
                     ResourceCategory.BROWSER_EXTENSION,
                     "Chrome extension integrating ChatGPT into every text box",
                     ["chrome", "browser"], 9000),
            Resource("cursor", "https://cursor.sh",
                     ResourceCategory.IDE_PLUGIN,
                     "AI-first code editor", ["ide", "ai"], 40000),
            Resource("awesome-chatgpt-prompts", "https://github.com/f/awesome-chatgpt-prompts",
                     ResourceCategory.PROMPT_LIBRARY,
                     "Curated ChatGPT prompt collection", ["prompts"], 100000),
            Resource("chatgpt-telegram-bot", "https://github.com/n3d1117/chatgpt-telegram-bot",
                     ResourceCategory.CHATBOT,
                     "Telegram bot powered by ChatGPT", ["telegram", "bot"], 4000),
            Resource("chroma", "https://github.com/chroma-core/chroma",
                     ResourceCategory.EMBEDDING_DB,
                     "AI-native open-source embedding database", ["vector", "embeddings"], 12000),
        ]
        self._resources.extend(seeds)

    def add_resource(self, resource: Resource) -> Result:
        """Add a resource to the catalog.

        Args:
            resource: Resource instance.

        Returns:
            Result monad.
        """
        existing = [r for r in self._resources if r.url == resource.url]
        if existing:
            return Err(f"Resource with URL '{resource.url}' already exists")
        self._resources.append(resource)
        return Ok(resource.name)

    def search(self, query: Optional[str] = None,
               category: Optional[ResourceCategory] = None,
               language: Optional[str] = None,
               limit: int = 20) -> List[Resource]:
        """Search the catalog.

        Args:
            query: Text query to match in name/description.
            category: Filter by category.
            language: Filter by programming language.
            limit: Max results.

        Returns:
            Filtered and sorted list of Resources.
        """
        results = list(self._resources)
        if category:
            results = [r for r in results if r.category == category]
        if language:
            lang_low = language.lower()
            results = [r for r in results if r.language.lower() == lang_low]
        if query:
            q_low = query.lower()
            results = [r for r in results
                       if q_low in r.name.lower() or q_low in r.description.lower()
                       or any(q_low in t.lower() for t in r.tags)]
        results.sort(key=lambda r: r.stars, reverse=True)
        return results[:limit]

    @property
    def total_resources(self) -> int:
        """Total resource count."""
        return len(self._resources)


# ---------------------------------------------------------------------------
# 4. PROMPT TEMPLATE ENGINE
# ---------------------------------------------------------------------------

class PromptEngine:
    """Manages reusable prompt templates with variable interpolation."""

    def diagnostics(self):
        """Return engine health diagnostics."""
        return {
            "engine": "PromptEngine",
            "status": "operational" if getattr(self, "is_active", True) else "inactive",
            "engine_id": getattr(self, "engine_id", "unknown"),
            "version": "1.0.0",
        }

    def __init__(self) -> None:
        """Initialise with built-in templates."""
        self._templates: Dict[str, PromptTemplate] = {}
        self._seed_templates()

    def _seed_templates(self) -> None:
        """Populate with common templates."""
        templates = [
            PromptTemplate("code_review", "Review this {language} code and suggest improvements:\n\n```{language}\n{code}\n```",
                           ["language", "code"], "development"),
            PromptTemplate("summarize", "Summarize the following text in {num_sentences} sentences:\n\n{text}",
                           ["num_sentences", "text"], "writing"),
            PromptTemplate("translate", "Translate the following text from {source_lang} to {target_lang}:\n\n{text}",
                           ["source_lang", "target_lang", "text"], "translation"),
            PromptTemplate("explain", "Explain {topic} as if I'm a {audience}.",
                           ["topic", "audience"], "education"),
        ]
        for t in templates:
            self._templates[t.name] = t

    def add_template(self, name: str, template: str,
                     parameters: List[str],
                     category: str = "general") -> Result:
        """Register a prompt template.

        Args:
            name: Template name.
            template: Template string with {param} placeholders.
            parameters: List of parameter names.
            category: Template category.

        Returns:
            Result monad.
        """
        if name in self._templates:
            return Err(f"Template '{name}' already exists")
        self._templates[name] = PromptTemplate(name, template, parameters, category)
        return Ok(name)

    def render(self, name: str, **kwargs: str) -> Result:
        """Render a prompt template with given parameters.

        Args:
            name: Template name.
            **kwargs: Parameter values.

        Returns:
            Result containing rendered prompt string.
        """
        tmpl = self._templates.get(name)
        if tmpl is None:
            return Err(f"Template '{name}' not found")
        missing = [p for p in tmpl.parameters if p not in kwargs]
        if missing:
            return Err(f"Missing parameters: {missing}")
        try:
            rendered = tmpl.template.format(**kwargs)
            return Ok(rendered)
        except KeyError as exc:
            return Err(f"Template rendering failed: {exc}")

    def list_templates(self) -> List[Dict[str, Any]]:
        """List all registered templates.

        Returns:
            List of template dicts.
        """
        return [{"name": t.name, "category": t.category,
                 "parameters": t.parameters}
                for t in self._templates.values()]


# ---------------------------------------------------------------------------
# 5. OMNI ENGINE CLASS
# ---------------------------------------------------------------------------

class OmniAwesomeChatgptEngine:
    """
    Production Engine aggregating ChatGPT ecosystem resources,
    SDK catalog, and prompt template management.
    """
    VERSION = "1.0.0"
    ENGINE_ID = "omni-awesome-chatgpt"

    def __init__(self) -> None:
        """Initialise the Awesome ChatGPT engine."""
        self.catalog = ResourceCatalog()
        self.prompts = PromptEngine()

    def search_resources(self, query: Optional[str] = None,
                         category: Optional[str] = None,
                         language: Optional[str] = None) -> Result:
        """Search the ChatGPT resource catalog.

        Args:
            query: Text query.
            category: Category filter string.
            language: Programming language filter.

        Returns:
            Result with list of resource dicts.
        """
        cat_enum = None
        if category:
            try:
                cat_enum = ResourceCategory(category)
            except ValueError:
                return Err(f"Unknown category: {category}")
        results = self.catalog.search(query=query, category=cat_enum,
                                       language=language)
        return Ok([{"name": r.name, "url": r.url, "category": r.category.value,
                     "description": r.description, "stars": r.stars}
                    for r in results])

    def render_prompt(self, template_name: str, **params: str) -> Result:
        """Render a prompt template.

        Args:
            template_name: Template name.
            **params: Template parameters.

        Returns:
            Result with rendered prompt string.
        """
        return self.prompts.render(template_name, **params)

    def list_prompt_templates(self) -> Result:
        """List all available prompt templates.

        Returns:
            Result with template list.
        """
        return Ok(self.prompts.list_templates())

    def diagnostics(self) -> Dict[str, Any]:
        """Return engine diagnostics.

        Returns:
            Dict with engine status.
        """
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "status": "operational",
            "resources_cataloged": self.catalog.total_resources,
            "prompt_templates": len(self.prompts._templates),
            "features": [
                "resource_catalog", "multi_language_sdk_search",
                "prompt_template_engine", "integration_discovery",
            ],
        }
