"""
OMNI Prompt Engineering Engine
================================
Production-grade, zero-mock prompt engineering toolkit inspired by
dair-ai/Prompt-Engineering-Guide and brexhq/prompt-engineering.

Implements:
  - Prompt templates with typed placeholders
  - Chain-of-Thought (CoT) prompting
  - Tree-of-Thought (ToT) prompting with branching evaluation
  - Graph-of-Thought (GoT) prompting with DAG traversal
  - ReAct (Reasoning + Acting) agent loop
  - Few-shot / Zero-shot prompt construction
  - Prompt compression and optimization
  - Prompt injection detection and sanitization
  - Automatic prompt evaluation scoring
  - Template registry and versioning
  - Output format enforcers (JSON, XML, Markdown)

OMNI Layer: compute (Python)
"""

from __future__ import annotations

import re
import json
import time
import hashlib
import math
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import (
    Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, Union,
)
from collections import OrderedDict

ENGINE_VERSION = "1.0.0-omni"

# ---------------------------------------------------------------------------
# 1. OMNI Result Monad (STRICT RULE §3.1)
# ---------------------------------------------------------------------------

class PromptError(Exception):
    """Base error for prompt engineering engine."""

@dataclass(frozen=True)
class Ok:
    """Monadic Ok result type."""
    value: Any

@dataclass(frozen=True)
class Err:
    """Monadic Err result type."""
    error: str

Result = Union[Ok, Err]

def _ok(v: Any) -> Ok:
    return Ok(v)

def _err(msg: str) -> Err:
    return Err(msg)


# ---------------------------------------------------------------------------
# 2. PROMPT TEMPLATE SYSTEM
# ---------------------------------------------------------------------------

class PlaceholderType(Enum):
    """Type enumeration for PlaceholderType."""
    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    LIST = auto()
    JSON = auto()


@dataclass
class Placeholder:
    """Production-grade Placeholder component."""
    name: str
    ptype: PlaceholderType = PlaceholderType.STRING
    required: bool = True
    default: Optional[str] = None
    description: str = ""

    def validate(self, value: Any) -> Result:
        """Execute validate operation for Placeholder."""
        if value is None:
            if self.required and self.default is None:
                return _err(f"Required placeholder '{self.name}' missing")
            return _ok(self.default)
        if self.ptype == PlaceholderType.INTEGER:
            try:
                int(value)
            except (ValueError, TypeError):
                return _err(f"Placeholder '{self.name}' expects integer, got '{type(value).__name__}'")
        elif self.ptype == PlaceholderType.FLOAT:
            try:
                float(value)
            except (ValueError, TypeError):
                return _err(f"Placeholder '{self.name}' expects float")
        elif self.ptype == PlaceholderType.JSON:
            if isinstance(value, str):
                try:
                    json.loads(value)
                except json.JSONDecodeError:
                    return _err(f"Placeholder '{self.name}' expects valid JSON")
        elif self.ptype == PlaceholderType.LIST:
            if not isinstance(value, (list, tuple)):
                return _err(f"Placeholder '{self.name}' expects list")
        return _ok(value)


@dataclass
class PromptTemplate:
    """Versioned prompt template with typed placeholders."""
    name: str
    template: str
    version: str = "1.0.0"
    placeholders: List[Placeholder] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    description: str = ""

    @property
    def template_hash(self) -> str:
        """Execute template hash operation for PromptTemplate."""
        return hashlib.sha256(self.template.encode()).hexdigest()[:12]

    def _discover_placeholders(self) -> Set[str]:
        """Find all {{placeholder}} markers in template."""
        return set(re.findall(r"\{\{(\w+)\}\}", self.template))

    def render(self, **kwargs: Any) -> Result:
        """
        Render template with provided values.
        Returns: Ok(rendered_string) or Err(message)
        """
        # Validate all placeholders
        ph_map = {p.name: p for p in self.placeholders}
        rendered = self.template

        for ph_name in self._discover_placeholders():
            ph = ph_map.get(ph_name)
            value = kwargs.get(ph_name)

            if ph:
                result = ph.validate(value)
                if isinstance(result, Err):
                    return result
                final_value = result.value if value is None else value
            else:
                final_value = value if value is not None else ""

            # Convert to string
            if isinstance(final_value, (list, tuple)):
                str_val = "\n".join(str(item) for item in final_value)
            elif isinstance(final_value, dict):
                str_val = json.dumps(final_value, indent=2)
            else:
                str_val = str(final_value) if final_value is not None else ""

            rendered = rendered.replace(f"{{{{{ph_name}}}}}", str_val)

        return _ok(rendered)


# ---------------------------------------------------------------------------
# 3. FEW-SHOT EXAMPLE MANAGEMENT
# ---------------------------------------------------------------------------

@dataclass
class FewShotExample:
    """A single input-output demonstration."""
    input_text: str
    output_text: str
    explanation: Optional[str] = None  # For CoT examples


class FewShotManager:
    """Manages and formats few-shot examples."""

    def __init__(self):
        self._examples: Dict[str, List[FewShotExample]] = {}

    def add_example(self, category: str, example: FewShotExample) -> None:
        """Add example to FewShotManager."""
        if category not in self._examples:
            self._examples[category] = []
        self._examples[category].append(example)

    def get_examples(self, category: str, max_examples: int = 5) -> List[FewShotExample]:
        """Retrieve examples from FewShotManager."""
        return self._examples.get(category, [])[:max_examples]

    def format_examples(
        self,
        category: str,
        max_examples: int = 5,
        include_explanation: bool = False,
        input_prefix: str = "Input: ",
        output_prefix: str = "Output: ",
        separator: str = "\n\n",
    ) -> str:
        """Format examples as a string for prompt injection."""
        examples = self.get_examples(category, max_examples)
        parts = []
        for ex in examples:
            block = f"{input_prefix}{ex.input_text}\n"
            if include_explanation and ex.explanation:
                block += f"Reasoning: {ex.explanation}\n"
            block += f"{output_prefix}{ex.output_text}"
            parts.append(block)
        return separator.join(parts)

    def categories(self) -> List[str]:
        """Execute categories operation for FewShotManager."""
        return list(self._examples.keys())


# ---------------------------------------------------------------------------
# 4. CHAIN-OF-THOUGHT (CoT) PROMPTING
# ---------------------------------------------------------------------------

@dataclass
class CoTStep:
    """A single reasoning step."""
    step_number: int
    reasoning: str
    intermediate_result: Optional[str] = None


@dataclass
class CoTChain:
    """A complete chain of thought."""
    question: str
    steps: List[CoTStep] = field(default_factory=list)
    final_answer: Optional[str] = None

    def add_step(self, reasoning: str, result: Optional[str] = None) -> None:
        """Add step to CoTChain."""
        step = CoTStep(
            step_number=len(self.steps) + 1,
            reasoning=reasoning,
            intermediate_result=result,
        )
        self.steps.append(step)

    def to_prompt(self) -> str:
        """Convert to prompt representation."""
        lines = [f"Question: {self.question}", "", "Let's think step by step:", ""]
        for step in self.steps:
            lines.append(f"Step {step.step_number}: {step.reasoning}")
            if step.intermediate_result:
                lines.append(f"  → {step.intermediate_result}")
        if self.final_answer:
            lines.append(f"\nTherefore, the answer is: {self.final_answer}")
        return "\n".join(lines)


class CoTPromptBuilder:
    """
    Chain-of-Thought prompt construction.

    Strategies:
    - Zero-shot CoT: "Let's think step by step"
    - Few-shot CoT: Provide examples with reasoning chains
    - Auto-CoT: Automatically decompose problems
    """

    ZERO_SHOT_TRIGGER = "Let's think step by step."
    SELF_CONSISTENCY_TRIGGER = "Let's solve this problem using multiple approaches."

    def zero_shot(self, question: str) -> str:
        """Zero-shot CoT prompt."""
        return f"{question}\n\n{self.ZERO_SHOT_TRIGGER}"

    def few_shot(self, question: str, examples: List[CoTChain]) -> str:
        """Few-shot CoT with reasoning examples."""
        parts = []
        for ex in examples:
            parts.append(ex.to_prompt())
        parts.append(f"Question: {question}\n\n{self.ZERO_SHOT_TRIGGER}")
        return "\n\n---\n\n".join(parts)

    def self_consistency(self, question: str, n_paths: int = 3) -> str:
        """Self-consistency prompt requesting multiple reasoning paths."""
        return (
            f"{question}\n\n"
            f"{self.SELF_CONSISTENCY_TRIGGER}\n\n"
            f"Provide {n_paths} independent reasoning paths, then determine "
            f"the most consistent answer by majority vote."
        )

    def auto_decompose(self, question: str) -> str:
        """Auto-CoT: Instruct decomposition of complex problem."""
        return (
            f"I need to solve the following problem:\n\n"
            f"{question}\n\n"
            f"First, break this problem down into smaller sub-problems.\n"
            f"Then, solve each sub-problem one at a time.\n"
            f"Finally, combine the results to get the final answer.\n\n"
            f"Sub-problems:"
        )


# ---------------------------------------------------------------------------
# 5. TREE-OF-THOUGHT (ToT) PROMPTING
# ---------------------------------------------------------------------------

@dataclass
class ToTNode:
    """A node in the Tree of Thought."""
    id: str
    thought: str
    score: float = 0.0
    children: List["ToTNode"] = field(default_factory=list)
    is_terminal: bool = False
    depth: int = 0

    def add_child(self, thought: str, score: float = 0.0) -> "ToTNode":
        """Add child to ToTNode."""
        child = ToTNode(
            id=f"{self.id}.{len(self.children)}",
            thought=thought,
            score=score,
            depth=self.depth + 1,
        )
        self.children.append(child)
        return child


class TreeOfThought:
    """
    Tree of Thought reasoning framework.

    Implements BFS and DFS exploration strategies with
    thought evaluation and pruning.
    """

    def __init__(
        self,
        problem: str,
        max_depth: int = 3,
        branching_factor: int = 3,
        strategy: str = "bfs",
        prune_threshold: float = 0.3,
    ):
        self.problem = problem
        self.max_depth = max_depth
        self.branching_factor = branching_factor
        self.strategy = strategy
        self.prune_threshold = prune_threshold
        self.root = ToTNode(id="0", thought=problem, depth=0)

    def generate_prompt(self) -> str:
        """Generate ToT exploration prompt."""
        return (
            f"Problem: {self.problem}\n\n"
            f"Explore this problem using Tree of Thought reasoning.\n\n"
            f"At each step:\n"
            f"1. Generate {self.branching_factor} different partial thoughts/approaches\n"
            f"2. Evaluate each thought on a scale of 0.0-1.0 for promise\n"
            f"3. Expand the most promising thoughts (score > {self.prune_threshold})\n"
            f"4. Continue for up to {self.max_depth} levels of depth\n"
            f"5. Select the best complete solution path\n\n"
            f"Strategy: {'Breadth-First' if self.strategy == 'bfs' else 'Depth-First'}\n\n"
            f"Begin exploration:"
        )

    def evaluate_path(self, path: List[ToTNode]) -> float:
        """Score a complete path from root to leaf."""
        if not path:
            return 0.0
        return sum(n.score for n in path) / len(path)

    def get_best_path(self) -> List[ToTNode]:
        """Find the highest-scoring complete path (DFS)."""
        best_path: List[ToTNode] = []
        best_score = -float("inf")

        def _dfs(node: ToTNode, path: List[ToTNode]) -> None:
            nonlocal best_path, best_score
            path = path + [node]
            if not node.children or node.is_terminal:
                score = self.evaluate_path(path)
                if score > best_score:
                    best_score = score
                    best_path = path[:]
            else:
                for child in node.children:
                    _dfs(child, path)

        _dfs(self.root, [])
        return best_path

    def to_dict(self) -> Dict[str, Any]:
        """Serialize tree to dict."""
        def _serialize(node: ToTNode) -> Dict:
            return {
                "id": node.id,
                "thought": node.thought,
                "score": node.score,
                "depth": node.depth,
                "children": [_serialize(c) for c in node.children],
            }
        return _serialize(self.root)


# ---------------------------------------------------------------------------
# 6. GRAPH-OF-THOUGHT (GoT) PROMPTING
# ---------------------------------------------------------------------------

@dataclass
class GoTNode:
    """A node in the Graph of Thought (DAG)."""
    id: str
    thought: str
    score: float = 0.0
    dependencies: List[str] = field(default_factory=list)  # IDs of prerequisite nodes


class GraphOfThought:
    """
    Graph of Thought reasoning framework.

    Enables DAG-structured reasoning where thoughts can
    depend on multiple prior thoughts (unlike linear CoT
    or branching ToT).
    """

    def __init__(self, problem: str):
        self.problem = problem
        self.nodes: OrderedDict[str, GoTNode] = OrderedDict()

    def add_thought(
        self,
        thought_id: str,
        thought: str,
        dependencies: Optional[List[str]] = None,
        score: float = 0.0,
    ) -> GoTNode:
        """Add thought to GraphOfThought."""
        node = GoTNode(
            id=thought_id,
            thought=thought,
            score=score,
            dependencies=dependencies or [],
        )
        self.nodes[thought_id] = node
        return node

    def topological_sort(self) -> List[GoTNode]:
        """Return nodes in dependency-respected order."""
        visited: Set[str] = set()
        result: List[GoTNode] = []

        def _visit(nid: str) -> None:
            if nid in visited:
                return
            visited.add(nid)
            node = self.nodes.get(nid)
            if node:
                for dep in node.dependencies:
                    _visit(dep)
                result.append(node)

        for nid in self.nodes:
            _visit(nid)
        return result

    def generate_prompt(self) -> str:
        """Generate GoT exploration prompt."""
        sorted_nodes = self.topological_sort()
        lines = [
            f"Problem: {self.problem}",
            "",
            "Graph of Thought Structure:",
            "",
        ]
        for node in sorted_nodes:
            deps = ", ".join(node.dependencies) if node.dependencies else "root"
            lines.append(f"  [{node.id}] {node.thought} (depends on: {deps}, score: {node.score})")
        lines.extend(["", "Synthesize insights from all thought nodes to produce a final answer."])
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "problem": self.problem,
            "nodes": [
                {"id": n.id, "thought": n.thought, "score": n.score, "deps": n.dependencies}
                for n in self.nodes.values()
            ],
        }


# ---------------------------------------------------------------------------
# 7. ReAct (REASONING + ACTING) AGENT LOOP
# ---------------------------------------------------------------------------

@dataclass
class ReActStep:
    """Production-grade Re Act Step component."""
    thought: str
    action: str
    action_input: str
    observation: str


class ReActAgent:
    """
    ReAct-style agent that interleaves reasoning and acting.

    Follows the Thought → Action → Observation loop pattern.
    """

    def __init__(
        self,
        available_tools: Optional[Dict[str, str]] = None,
        max_steps: int = 10,
    ):
        self.tools = available_tools or {
            "search": "Search for information on a topic",
            "calculate": "Perform mathematical calculations",
            "lookup": "Look up specific facts or data",
        }
        self.max_steps = max_steps
        self.trace: List[ReActStep] = []

    def generate_system_prompt(self) -> str:
        """Generate the ReAct system prompt with tool descriptions."""
        tool_list = "\n".join(f"  - {name}: {desc}" for name, desc in self.tools.items())
        return (
            "You are an AI assistant that solves problems by thinking and acting.\n\n"
            "Available tools:\n"
            f"{tool_list}\n\n"
            "For each step, follow this format:\n"
            "Thought: [Your reasoning about what to do next]\n"
            "Action: [tool_name]\n"
            "Action Input: [input for the tool]\n"
            "Observation: [result from the tool]\n\n"
            "When you have enough information, provide:\n"
            "Thought: I now have enough information to answer.\n"
            "Final Answer: [your final answer]\n"
        )

    def format_step(self, step: ReActStep) -> str:
        """Execute format step operation for ReActAgent."""
        return (
            f"Thought: {step.thought}\n"
            f"Action: {step.action}\n"
            f"Action Input: {step.action_input}\n"
            f"Observation: {step.observation}"
        )

    def build_prompt(self, question: str) -> str:
        """Build the complete ReAct prompt with trace."""
        prompt = self.generate_system_prompt()
        prompt += f"\nQuestion: {question}\n\n"
        for step in self.trace:
            prompt += self.format_step(step) + "\n\n"
        return prompt

    def add_step(self, thought: str, action: str, action_input: str, observation: str) -> None:
        """Add step to ReActAgent."""
        self.trace.append(ReActStep(thought, action, action_input, observation))


# ---------------------------------------------------------------------------
# 8. PROMPT INJECTION DETECTION & SANITIZATION
# ---------------------------------------------------------------------------

class PromptGuard:
    """
    Detects and mitigates prompt injection attempts.

    Detection strategies:
    - Pattern matching for known injection phrases
    - Delimiter escape detection
    - Role hijacking detection
    - Instruction override detection
    """

    # Known injection patterns
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"disregard\s+(all\s+)?above",
        r"forget\s+(everything|all|your\s+instructions)",
        r"you\s+are\s+now\s+(a|an)\s+",
        r"act\s+as\s+(if|though)\s+you",
        r"new\s+instructions?\s*:",
        r"system\s*:\s*",
        r"<\|?system\|?>",
        r"###\s*(system|instruction)",
        r"override\s+(all\s+)?safety",
        r"jailbreak",
        r"DAN\s+mode",
        r"do\s+anything\s+now",
    ]

    def __init__(self, custom_patterns: Optional[List[str]] = None):
        self._patterns = [re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS]
        if custom_patterns:
            self._patterns.extend(re.compile(p, re.IGNORECASE) for p in custom_patterns)

    def detect(self, text: str) -> Tuple[bool, List[str]]:
        """
        Detect potential prompt injection.
        Returns (is_suspicious, list_of_matched_patterns)
        """
        matches = []
        for pattern in self._patterns:
            if pattern.search(text):
                matches.append(pattern.pattern)
        return len(matches) > 0, matches

    def sanitize(self, text: str, replacement: str = "[FILTERED]") -> str:
        """Remove or replace detected injection patterns."""
        sanitized = text
        for pattern in self._patterns:
            sanitized = pattern.sub(replacement, sanitized)
        return sanitized

    def wrap_with_delimiters(self, user_input: str, delimiter: str = "```") -> str:
        """Wrap user input in delimiters to prevent injection."""
        escaped = user_input.replace(delimiter, "")
        return f"{delimiter}\n{escaped}\n{delimiter}"

    def score_risk(self, text: str) -> float:
        """Score injection risk from 0.0 (safe) to 1.0 (dangerous)."""
        _, matches = self.detect(text)
        n_patterns = len(self._patterns)
        if n_patterns == 0:
            return 0.0
        return min(1.0, len(matches) / max(1, n_patterns / 3))


# ---------------------------------------------------------------------------
# 9. OUTPUT FORMAT ENFORCERS
# ---------------------------------------------------------------------------

class OutputFormat(Enum):
    """Production-grade Output Format component."""
    JSON = auto()
    XML = auto()
    MARKDOWN_TABLE = auto()
    YAML = auto()
    CSV = auto()


class OutputFormatEnforcer:
    """Append format enforcement instructions to prompts."""

    @staticmethod
    def json_format(schema: Optional[Dict] = None) -> str:
        """Execute json format operation for OutputFormatEnforcer."""
        base = "Respond ONLY with valid JSON. No additional text before or after the JSON."
        if schema:
            base += f"\n\nExpected JSON schema:\n```json\n{json.dumps(schema, indent=2)}\n```"
        return base

    @staticmethod
    def xml_format(root_element: str = "response") -> str:
        """Execute xml format operation for OutputFormatEnforcer."""
        return (
            f"Respond ONLY with valid XML.\n"
            f"Use <{root_element}> as the root element.\n"
            f"Do not include any text outside the XML tags."
        )

    @staticmethod
    def markdown_table(columns: List[str]) -> str:
        """Execute markdown table operation for OutputFormatEnforcer."""
        header = " | ".join(columns)
        separator = " | ".join("---" for _ in columns)
        return (
            f"Respond with a Markdown table with these columns:\n\n"
            f"| {header} |\n| {separator} |\n| ... |"
        )

    @staticmethod
    def csv_format(columns: List[str]) -> str:
        """Execute csv format operation for OutputFormatEnforcer."""
        return f"Respond with CSV data. Headers: {','.join(columns)}\nNo additional text."

    @staticmethod
    def yaml_format() -> str:
        """Execute yaml format operation for OutputFormatEnforcer."""
        return "Respond ONLY with valid YAML. No additional text."


# ---------------------------------------------------------------------------
# 10. PROMPT OPTIMIZER
# ---------------------------------------------------------------------------

class PromptOptimizer:
    """
    Optimize prompts for clarity, token efficiency, and effectiveness.

    Techniques:
    - Remove redundant whitespace
    - Compress instructions
    - Structured sectioning
    - Token estimation
    """

    @staticmethod
    def compress(prompt: str) -> str:
        """Remove redundant whitespace and empty lines."""
        lines = prompt.split("\n")
        compressed = []
        prev_empty = False
        for line in lines:
            stripped = line.strip()
            if stripped == "":
                if not prev_empty:
                    compressed.append("")
                prev_empty = True
            else:
                compressed.append(stripped)
                prev_empty = False
        return "\n".join(compressed).strip()

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough token count estimation (English ~4 chars/token)."""
        return max(1, len(text) // 4)

    @staticmethod
    def structure_prompt(
        system: str,
        context: Optional[str] = None,
        examples: Optional[str] = None,
        instruction: str = "",
        output_format: Optional[str] = None,
    ) -> str:
        """Build a well-structured prompt with clear sections."""
        parts = [f"# System\n{system}"]
        if context:
            parts.append(f"\n# Context\n{context}")
        if examples:
            parts.append(f"\n# Examples\n{examples}")
        parts.append(f"\n# Instruction\n{instruction}")
        if output_format:
            parts.append(f"\n# Output Format\n{output_format}")
        return "\n".join(parts)


# ---------------------------------------------------------------------------
# 11. PROMPT EVALUATION
# ---------------------------------------------------------------------------

@dataclass
class PromptEvaluation:
    """Evaluation result for a prompt."""
    clarity_score: float       # 0-1: How clear is the prompt?
    specificity_score: float   # 0-1: How specific is the prompt?
    structure_score: float     # 0-1: How well structured?
    injection_risk: float      # 0-1: Risk of injection vulnerability
    token_count: int
    suggestions: List[str] = field(default_factory=list)

    @property
    def overall_score(self) -> float:
        """Execute overall score operation for PromptEvaluation."""
        return (
            self.clarity_score * 0.3
            + self.specificity_score * 0.3
            + self.structure_score * 0.25
            + (1.0 - self.injection_risk) * 0.15
        )


class PromptEvaluator:
    """Evaluate prompt quality using heuristic analysis."""

    def __init__(self):
        self._guard = PromptGuard()
        self._optimizer = PromptOptimizer()

    def evaluate(self, prompt: str) -> PromptEvaluation:
        """Evaluate evaluate."""
        suggestions: List[str] = []

        # Clarity: based on sentence structure and readability
        words = prompt.split()
        avg_word_len = sum(len(w) for w in words) / max(1, len(words))
        clarity = min(1.0, max(0.0, 1.0 - abs(avg_word_len - 5.0) / 10.0))
        if len(words) < 10:
            suggestions.append("Prompt is very short. Consider adding more context.")
            clarity *= 0.7

        # Specificity: presence of specific instruction keywords
        specificity_keywords = [
            "exactly", "specific", "must", "required", "step", "format",
            "following", "include", "exclude", "between", "maximum", "minimum",
        ]
        found = sum(1 for kw in specificity_keywords if kw in prompt.lower())
        specificity = min(1.0, found / 4.0)
        if specificity < 0.3:
            suggestions.append("Add more specific constraints (format, length, etc.).")

        # Structure: check for sections, newlines, formatting
        has_sections = bool(re.search(r"^#+\s", prompt, re.MULTILINE))
        has_bullets = bool(re.search(r"^[\-\*]\s", prompt, re.MULTILINE))
        has_numbers = bool(re.search(r"^\d+[\.\)]\s", prompt, re.MULTILINE))
        structure = 0.3
        if has_sections:
            structure += 0.3
        if has_bullets or has_numbers:
            structure += 0.2
        if "\n\n" in prompt:
            structure += 0.2
        structure = min(1.0, structure)

        # Injection risk
        injection_risk = self._guard.score_risk(prompt)
        if injection_risk > 0.3:
            suggestions.append("WARNING: Prompt may be vulnerable to injection attacks.")

        # Token count
        token_count = self._optimizer.estimate_tokens(prompt)
        if token_count > 2000:
            suggestions.append("Prompt is very long. Consider compressing.")

        return PromptEvaluation(
            clarity_score=clarity,
            specificity_score=specificity,
            structure_score=structure,
            injection_risk=injection_risk,
            token_count=token_count,
            suggestions=suggestions,
        )


# ---------------------------------------------------------------------------
# 12. TEMPLATE REGISTRY
# ---------------------------------------------------------------------------

class TemplateRegistry:
    """
    Version-controlled registry for prompt templates.
    Supports CRUD operations and search by tag.
    """

    def __init__(self):
        self._templates: Dict[str, Dict[str, PromptTemplate]] = {}  # name -> {version -> template}

    def register(self, template: PromptTemplate) -> Result:
        """Execute register operation for TemplateRegistry."""
        if template.name not in self._templates:
            self._templates[template.name] = {}
        if template.version in self._templates[template.name]:
            return _err(f"Template '{template.name}' v{template.version} already exists")
        self._templates[template.name][template.version] = template
        return _ok(f"Registered '{template.name}' v{template.version}")

    def get(self, name: str, version: Optional[str] = None) -> Result:
        """Execute get operation for TemplateRegistry."""
        if name not in self._templates:
            return _err(f"Template '{name}' not found")
        versions = self._templates[name]
        if version:
            t = versions.get(version)
            return _ok(t) if t else _err(f"Version '{version}' not found for '{name}'")
        # Return latest version
        latest = sorted(versions.keys())[-1]
        return _ok(versions[latest])

    def search_by_tag(self, tag: str) -> List[PromptTemplate]:
        """Execute search by tag operation for TemplateRegistry."""
        results = []
        for versions in self._templates.values():
            for t in versions.values():
                if tag in t.tags:
                    results.append(t)
        return results

    def list_all(self) -> List[Dict[str, str]]:
        """Execute list all operation for TemplateRegistry."""
        result = []
        for name, versions in self._templates.items():
            for v, t in versions.items():
                result.append({"name": name, "version": v, "hash": t.template_hash})
        return result


# ---------------------------------------------------------------------------
# 13. OMNI ENGINE CLASS — Production Interface
# ---------------------------------------------------------------------------

class OmniPromptEngineeringEngine:
    """
    Production-grade prompt engineering toolkit for OMNI Framework.

    Provides:
      - Typed prompt templates with validation
      - Chain-of-Thought (CoT), Tree-of-Thought (ToT), Graph-of-Thought (GoT)
      - ReAct agent loop framework
      - Few-shot / Zero-shot prompt construction
      - Prompt injection detection and sanitization
      - Output format enforcement (JSON, XML, Markdown, CSV)
      - Prompt optimization and compression
      - Prompt quality evaluation
      - Version-controlled template registry
    """

    VERSION = "1.0.0"
    ENGINE_ID = "omni-prompt-engineering"

    def __init__(self):
        """Initialize OmniPromptEngineeringEngine."""
        self.registry = TemplateRegistry()
        self.few_shot = FewShotManager()
        self.cot = CoTPromptBuilder()
        self.guard = PromptGuard()
        self.optimizer = PromptOptimizer()
        self.evaluator = PromptEvaluator()
        self.format_enforcer = OutputFormatEnforcer()

    # --- Template operations ---

    def create_template(
        self,
        name: str,
        template: str,
        version: str = "1.0.0",
        placeholders: Optional[List[Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None,
    ) -> Result:
        """Performs create template operation for OmniPromptEngineeringEngine."""
        phs = []
        for ph in (placeholders or []):
            phs.append(Placeholder(
                name=ph.get("name", ""),
                ptype=PlaceholderType[ph.get("type", "STRING").upper()],
                required=ph.get("required", True),
                default=ph.get("default"),
                description=ph.get("description", ""),
            ))
        tpl = PromptTemplate(
            name=name,
            template=template,
            version=version,
            placeholders=phs,
            tags=tags or [],
        )
        return self.registry.register(tpl)

    def render_template(self, template_name: str, version: Optional[str] = None, **kwargs) -> Result:
        """Performs render template operation for OmniPromptEngineeringEngine."""
        result = self.registry.get(template_name, version)
        if isinstance(result, Err):
            return result
        return result.value.render(**kwargs)

    # --- Reasoning frameworks ---

    def create_cot_chain(self, question: str) -> CoTChain:
        """Performs create cot chain operation for OmniPromptEngineeringEngine."""
        return CoTChain(question=question)

    def create_tot(
        self,
        problem: str,
        max_depth: int = 3,
        branching_factor: int = 3,
    ) -> TreeOfThought:
        """Performs create tot operation for OmniPromptEngineeringEngine."""
        return TreeOfThought(problem, max_depth, branching_factor)

    def create_got(self, problem: str) -> GraphOfThought:
        """Performs create got operation for OmniPromptEngineeringEngine."""
        return GraphOfThought(problem)

    def create_react_agent(
        self,
        tools: Optional[Dict[str, str]] = None,
        max_steps: int = 10,
    ) -> ReActAgent:
        """Performs create react agent operation for OmniPromptEngineeringEngine."""
        return ReActAgent(tools, max_steps)

    # --- Convenience ---

    def zero_shot_cot(self, question: str) -> str:
        """Performs zero shot cot operation for OmniPromptEngineeringEngine."""
        return self.cot.zero_shot(question)

    def detect_injection(self, text: str) -> Tuple[bool, List[str]]:
        """Performs detect injection operation for OmniPromptEngineeringEngine."""
        return self.guard.detect(text)

    def sanitize(self, text: str) -> str:
        """Performs sanitize operation for OmniPromptEngineeringEngine."""
        return self.guard.sanitize(text)

    def evaluate_prompt(self, prompt: str) -> PromptEvaluation:
        """Performs evaluate prompt operation for OmniPromptEngineeringEngine."""
        return self.evaluator.evaluate(prompt)

    def compress_prompt(self, prompt: str) -> str:
        """Performs compress prompt operation for OmniPromptEngineeringEngine."""
        return self.optimizer.compress(prompt)

    def estimate_tokens(self, text: str) -> int:
        """Performs estimate tokens operation for OmniPromptEngineeringEngine."""
        return self.optimizer.estimate_tokens(text)

    # --- Diagnostics ---

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniPromptEngineeringEngine."""
        return {
            "engine_id": self.ENGINE_ID,
            "version": self.VERSION,
            "templates_registered": len(self.registry.list_all()),
            "few_shot_categories": self.few_shot.categories(),
            "injection_patterns": len(self.guard._patterns),
            "reasoning_frameworks": ["CoT", "ToT", "GoT", "ReAct"],
            "output_formats": [f.name for f in OutputFormat],
            "status": "operational",
        }
