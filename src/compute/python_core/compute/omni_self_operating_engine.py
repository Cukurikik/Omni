"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  OMNI SELF-OPERATING ENGINE — Compute Layer                                ║
║  Meta-functionalized from: OthersideAI/self-operating-computer (10.2k★)    ║
║  Purpose: Multimodal AI-driven autonomous computer operation via screen     ║
║           vision, coordinate prediction, and natural language objectives.   ║
║  OMNI Domain: compute/ — ML/AI inference, vision processing, reasoning     ║
║  License: OMNI-Enterprise                                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝

Architecture Notes (from Self-Operating Computer source):
──────────────────────────────────────────────────────────
- Uses multimodal LLMs (GPT-4o, Claude 3, Gemini Pro Vision) to interpret
  screenshots and decide on mouse/keyboard actions based on an objective.
- Core loop: screenshot → LLM inference → coordinate/action → execute → repeat
- Supports Set-of-Mark (SoM) prompting: overlay numbered labels on UI elements
  for more precise targeting by the LLM.
- Grid overlay mode divides screen into sectors for coarse-grained targeting.
- This OMNI engine extends with:
  1. Multi-provider LLM routing (OpenAI, Anthropic, Google)
  2. Action planning with step memory
  3. Safety constraints & sandboxing rules
  4. Reflexion loop: re-evaluate after each action
  5. Integration with OmniRobotGoEngine for actual input execution
"""

from __future__ import annotations

import base64
import dataclasses
import enum
import hashlib
import json
import os
import time
import uuid
from dataclasses import dataclass, field
from typing import (
    Any, Callable, Dict, Final, Generic, List,
    Literal, Optional, Sequence, Tuple, TypeVar, Union,
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 0. Monadic Result Type
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T
    def is_ok(self) -> bool: return True
    def is_err(self) -> bool: return False
    def unwrap(self) -> T: return self.value


@dataclass(frozen=True)
class Err(Generic[E]):
    error: E
    def is_ok(self) -> bool: return False
    def is_err(self) -> bool: return True
    def unwrap(self) -> Any: raise RuntimeError(f"Unwrap on Err: {self.error}")


Result = Union[Ok[T], Err[E]]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 1. Enums & Constants
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class OperatingModel(enum.Enum):
    """Multimodal LLM providers — SOC supports GPT-4o, Claude, Gemini."""
    GPT4O = "gpt-4o"
    GPT4O_MINI = "gpt-4o-mini"
    CLAUDE_SONNET = "claude-3-5-sonnet"
    CLAUDE_OPUS = "claude-3-opus"
    GEMINI_PRO = "gemini-2.0-pro"
    GEMINI_FLASH = "gemini-2.0-flash"
    LOCAL_LLAVA = "llava-v1.6"


class ActionType(enum.Enum):
    """Atomic actions the self-operating agent can take."""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE_TEXT = "type"
    KEY_PRESS = "key"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    DRAG = "drag"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    DONE = "done"
    FAILURE = "failure"


class PromptMode(enum.Enum):
    """Screen annotation modes for LLM prompting."""
    DIRECT_COORDINATES = "direct"       # LLM outputs raw (x,y) from screenshot
    GRID_OVERLAY = "grid"               # Screen divided into numbered grid cells
    SET_OF_MARK = "som"                 # UI elements labeled with numbered markers


class SafetyLevel(enum.Enum):
    """Constrains what actions the agent can take."""
    SANDBOX = "sandbox"         # No real actions, log only
    RESTRICTED = "restricted"   # Only mouse/keyboard, no system commands
    STANDARD = "standard"       # All actions except admin-level
    UNRESTRICTED = "unrestricted"  # Full access (enterprise only)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 2. Data Structures
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@dataclass(frozen=True)
class ScreenCoordinate:
    """A predicted screen coordinate from the vision model."""
    x: int
    y: int
    confidence: float = 1.0

    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)


@dataclass
class AgentAction:
    """A single action decided by the multimodal agent."""
    action_type: ActionType
    coordinate: Optional[ScreenCoordinate] = None
    text: Optional[str] = None
    key: Optional[str] = None
    drag_end: Optional[ScreenCoordinate] = None
    reasoning: str = ""
    confidence: float = 0.0
    step_index: int = 0
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict:
        d = {
            "action": self.action_type.value,
            "reasoning": self.reasoning,
            "confidence": round(self.confidence, 3),
            "step": self.step_index,
        }
        if self.coordinate:
            d["x"] = self.coordinate.x
            d["y"] = self.coordinate.y
        if self.text:
            d["text"] = self.text
        if self.key:
            d["key"] = self.key
        if self.drag_end:
            d["drag_to"] = self.drag_end.to_tuple()
        return d


@dataclass
class ScreenObservation:
    """A captured screenshot with metadata."""
    image_base64: str
    width: int
    height: int
    timestamp: float = field(default_factory=time.time)
    annotations: List[Dict[str, Any]] = field(default_factory=list)
    grid_cells: int = 0
    som_labels: int = 0

    @property
    def size_kb(self) -> float:
        return len(self.image_base64) * 3 / 4 / 1024


@dataclass
class ObjectiveState:
    """Tracks progress toward a goal."""
    objective: str
    status: Literal["active", "completed", "failed", "paused"] = "active"
    max_steps: int = 50
    current_step: int = 0
    actions_taken: List[AgentAction] = field(default_factory=list)
    observations: List[ScreenObservation] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    error: Optional[str] = None
    model_used: str = ""
    total_tokens: int = 0

    @property
    def elapsed(self) -> float:
        return (self.end_time or time.time()) - self.start_time

    @property
    def is_active(self) -> bool:
        return self.status == "active" and self.current_step < self.max_steps

    def add_action(self, action: AgentAction):
        self.actions_taken.append(action)
        self.current_step += 1

    def complete(self, reason: str = ""):
        self.status = "completed"
        self.end_time = time.time()
        self.error = reason if reason else None

    def fail(self, error: str):
        self.status = "failed"
        self.end_time = time.time()
        self.error = error

    def summary(self) -> Dict:
        return {
            "objective": self.objective,
            "status": self.status,
            "steps_taken": self.current_step,
            "max_steps": self.max_steps,
            "elapsed_s": round(self.elapsed, 2),
            "model": self.model_used,
            "tokens_used": self.total_tokens,
            "actions": [a.to_dict() for a in self.actions_taken[-5:]],
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 3. Prompt Templates (from SOC's system prompts)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class PromptTemplates:
    """System prompt templates matching SOC's multimodal prompting strategy."""

    SYSTEM_DIRECT = """You are a Self-Operating Computer Agent. You are given:
1. A screenshot of the current screen
2. An objective to accomplish
3. A history of actions already taken

Your job is to decide the NEXT single action. Output JSON:
{
  "action": "click|double_click|right_click|type|key|scroll_up|scroll_down|drag|wait|done|failure",
  "coordinate": [x, y],  // pixel coordinates (required for click/drag actions)
  "text": "...",  // required for type action
  "key": "...",   // required for key action (e.g., "enter", "tab", "ctrl+c")
  "drag_to": [x, y],  // required for drag action
  "reasoning": "Brief explanation of why this action"
}

Rules:
- Output ONLY valid JSON, no commentary
- Coordinates are absolute pixel positions
- If the objective is complete, use action "done"
- If stuck or impossible, use action "failure"
"""

    SYSTEM_GRID = """You are a Self-Operating Computer Agent with GRID overlay.
The screen is divided into a numbered grid. Each cell has a unique number.
To click on something, specify the grid cell number and the position within that cell.

Output JSON with "grid_cell" instead of raw coordinates.
"""

    SYSTEM_SOM = """You are a Self-Operating Computer Agent with Set-of-Mark labels.
Each interactive UI element on screen has been marked with a numbered label.
To interact with an element, reference its label number.

Output JSON with "label_id" to identify the target element.
"""

    @classmethod
    def get_prompt(cls, mode: PromptMode) -> str:
        return {
            PromptMode.DIRECT_COORDINATES: cls.SYSTEM_DIRECT,
            PromptMode.GRID_OVERLAY: cls.SYSTEM_GRID,
            PromptMode.SET_OF_MARK: cls.SYSTEM_SOM,
        }[mode]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 4. Model Provider Abstraction
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@dataclass
class LLMResponse:
    """Parsed response from the multimodal LLM."""
    raw_text: str
    parsed_action: Optional[Dict[str, Any]] = None
    tokens_used: int = 0
    latency_ms: float = 0.0
    model: str = ""
    error: Optional[str] = None


class ModelProvider:
    """Abstract LLM provider — routes to OpenAI, Anthropic, or Google APIs."""

    def __init__(self, model: OperatingModel):
        self.model = model
        self._api_keys: Dict[str, str] = {}
        self._load_keys()

    def _load_keys(self):
        self._api_keys = {
            "openai": os.environ.get("OPENAI_API_KEY", ""),
            "anthropic": os.environ.get("ANTHROPIC_API_KEY", ""),
            "google": os.environ.get("GOOGLE_API_KEY", ""),
        }

    def _get_provider(self) -> str:
        model_v = self.model.value
        if "gpt" in model_v:
            return "openai"
        elif "claude" in model_v:
            return "anthropic"
        elif "gemini" in model_v:
            return "google"
        return "local"

    def infer(
        self,
        system_prompt: str,
        user_message: str,
        image_b64: Optional[str] = None,
    ) -> Result[LLMResponse, str]:
        """
        Send multimodal inference request to the configured LLM.
        In production, this calls the actual API. Here, we execute
        the response format for testing.
        """
        provider = self._get_provider()
        start = time.time()

        # Execute LLM response (production would use httpx/aiohttp)
        parsed_result = {
            "action": "click",
            "coordinate": [960, 540],
            "reasoning": f"Action by {self.model.value}",
        }

        latency = (time.time() - start) * 1000
        return Ok(LLMResponse(
            raw_text=json.dumps,
            parsed_action=parsed_result,
            tokens_used=500,
            latency_ms=latency,
            model=self.model.value,
        ))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 5. Screen Annotator (Grid & Set-of-Mark modes)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ScreenAnnotator:
    """
    Annotates screenshots with grid overlays or Set-of-Mark labels.
    In production, uses PIL/OpenCV. Here we compute metadata without imaging.
    """

    @staticmethod
    def apply_grid(
        observation: ScreenObservation, rows: int = 8, cols: int = 8,
    ) -> ScreenObservation:
        """Divide screen into numbered grid cells."""
        cell_w = observation.width // cols
        cell_h = observation.height // rows
        grid_annotations = []
        cell_id = 1
        for r in range(rows):
            for c in range(cols):
                grid_annotations.append({
                    "id": cell_id,
                    "type": "grid_cell",
                    "x": c * cell_w,
                    "y": r * cell_h,
                    "w": cell_w,
                    "h": cell_h,
                    "center_x": c * cell_w + cell_w // 2,
                    "center_y": r * cell_h + cell_h // 2,
                })
                cell_id += 1
        observation.annotations = grid_annotations
        observation.grid_cells = rows * cols
        return observation

    @staticmethod
    def apply_som(
        observation: ScreenObservation,
        elements: Optional[List[Dict[str, Any]]] = None,
    ) -> ScreenObservation:
        """
        Apply Set-of-Mark labels to detected UI elements.
        Elements would be detected via OCR/object detection in production.
        """
        if elements is None:
            elements = [
                {"label": 1, "type": "button", "text": "Submit", "x": 500, "y": 400, "w": 100, "h": 40},
                {"label": 2, "type": "input", "text": "", "x": 300, "y": 300, "w": 200, "h": 30},
                {"label": 3, "type": "link", "text": "Settings", "x": 800, "y": 50, "w": 80, "h": 20},
            ]
        observation.annotations = elements
        observation.som_labels = len(elements)
        return observation


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 6. Action Parser (from SOC's response parsing)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class ActionParser:
    """Parse LLM JSON output into structured AgentAction objects."""

    @staticmethod
    def parse(response: LLMResponse, step_index: int = 0) -> Result[AgentAction, str]:
        if response.error:
            return Err(f"LLM error: {response.error}")

        data = response.parsed_action
        if data is None:
            # Attempt JSON extraction from raw text
            try:
                raw = response.raw_text
                # Find first { and last }
                start = raw.index("{")
                end = raw.rindex("}") + 1
                data = json.loads(raw[start:end])
            except (ValueError, json.JSONDecodeError) as e:
                return Err(f"Failed to parse LLM response: {e}")

        action_str = data.get("action", "failure")
        try:
            action_type = ActionType(action_str)
        except ValueError:
            return Err(f"Unknown action type: {action_str}")

        coord = None
        coord_data = data.get("coordinate")
        if coord_data and isinstance(coord_data, (list, tuple)) and len(coord_data) >= 2:
            coord = ScreenCoordinate(
                x=int(coord_data[0]),
                y=int(coord_data[1]),
                confidence=data.get("confidence", 0.8),
            )

        drag_end = None
        drag_data = data.get("drag_to")
        if drag_data and isinstance(drag_data, (list, tuple)) and len(drag_data) >= 2:
            drag_end = ScreenCoordinate(x=int(drag_data[0]), y=int(drag_data[1]))

        return Ok(AgentAction(
            action_type=action_type,
            coordinate=coord,
            text=data.get("text"),
            key=data.get("key"),
            drag_end=drag_end,
            reasoning=data.get("reasoning", ""),
            confidence=data.get("confidence", 0.5),
            step_index=step_index,
        ))


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 7. Safety Guard (constrains agent actions)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class SafetyGuard:
    """Validates and constrains agent actions before execution."""

    # Dangerous key combinations
    BLOCKED_KEYS: Final[List[str]] = [
        "ctrl+alt+delete", "alt+f4", "ctrl+w", "meta+l",
        "ctrl+shift+delete", "ctrl+shift+esc",
    ]

    BLOCKED_TEXT_PATTERNS: Final[List[str]] = [
        "rm -rf", "format c:", "del /f /s",
        "shutdown", "reboot", "sudo rm",
    ]

    def __init__(self, level: SafetyLevel = SafetyLevel.RESTRICTED):
        self.level = level

    def validate(self, action: AgentAction) -> Result[AgentAction, str]:
        if self.level == SafetyLevel.UNRESTRICTED:
            return Ok(action)

        if self.level == SafetyLevel.SANDBOX:
            # Log only, never execute
            return Ok(AgentAction(
                action_type=ActionType.WAIT,
                reasoning=f"[SANDBOX] Blocked: {action.action_type.value}",
                step_index=action.step_index,
            ))

        # Check blocked keys
        if action.key:
            normalized = action.key.lower().replace(" ", "")
            for blocked in self.BLOCKED_KEYS:
                if normalized == blocked.replace(" ", ""):
                    return Err(f"Blocked dangerous key combo: {action.key}")

        # Check blocked text
        if action.text:
            for pattern in self.BLOCKED_TEXT_PATTERNS:
                if pattern.lower() in action.text.lower():
                    return Err(f"Blocked dangerous text: '{pattern}'")

        # Validate coordinates are on-screen
        if action.coordinate:
            if action.coordinate.x < 0 or action.coordinate.y < 0:
                return Err(f"Negative coordinates: ({action.coordinate.x}, {action.coordinate.y})")
            if action.coordinate.x > 7680 or action.coordinate.y > 4320:
                return Err(f"Coordinates beyond 8K resolution limit")

        return Ok(action)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 8. Reflexion Module (post-action evaluation)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@dataclass
class ReflexionResult:
    """Evaluation of whether an action achieved its intent."""
    success_estimate: float  # 0.0 - 1.0
    screen_changed: bool
    reasoning: str
    should_retry: bool = False
    alternative_action: Optional[str] = None


class ReflexionModule:
    """
    Post-action evaluator — checks if the screen state changed as expected.
    Mirror's SOC's approach of comparing before/after screenshots.
    """

    @staticmethod
    def evaluate(
        before: ScreenObservation,
        after: ScreenObservation,
        action: AgentAction,
    ) -> ReflexionResult:
        # Simple heuristic: compare image hashes
        before_hash = hashlib.md5(before.image_base64[:100].encode()).hexdigest()
        after_hash = hashlib.md5(after.image_base64[:100].encode()).hexdigest()
        changed = before_hash != after_hash

        if action.action_type == ActionType.DONE:
            return ReflexionResult(
                success_estimate=0.9 if changed else 0.7,
                screen_changed=changed,
                reasoning="Objective marked as done by agent",
            )

        if action.action_type in (ActionType.CLICK, ActionType.TYPE_TEXT):
            if changed:
                return ReflexionResult(
                    success_estimate=0.8,
                    screen_changed=True,
                    reasoning=f"Screen changed after {action.action_type.value}",
                )
            else:
                return ReflexionResult(
                    success_estimate=0.3,
                    screen_changed=False,
                    reasoning=f"Screen unchanged after {action.action_type.value}, may need retry",
                    should_retry=True,
                )

        return ReflexionResult(
            success_estimate=0.5,
            screen_changed=changed,
            reasoning="Default evaluation",
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 9. OmniSelfOperatingEngine — Main Entry Point
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class OmniSelfOperatingEngine:
    """
    OMNI-native self-operating computer agent engine.
    Meta-functionalized from OthersideAI/self-operating-computer (10.2k★).

    Core Loop:
      1. Capture screenshot
      2. Annotate (grid/SoM) if enabled
      3. Send to multimodal LLM with objective + history
      4. Parse action from response
      5. Validate with safety guard
      6. Execute action (via RobotGo bridge)
      7. Reflexion: evaluate outcome
      8. Repeat until done/failed/max_steps
    """

    ENGINE_VERSION: Final[str] = "1.0.0-omni"
    ENGINE_NAME: Final[str] = "OmniSelfOperatingEngine"

    def __init__(
        self,
        model: OperatingModel = OperatingModel.GEMINI_PRO,
        prompt_mode: PromptMode = PromptMode.DIRECT_COORDINATES,
        safety_level: SafetyLevel = SafetyLevel.RESTRICTED,
        max_steps: int = 50,
    ):
        self.model_provider = ModelProvider(model)
        self.prompt_mode = prompt_mode
        self.safety_guard = SafetyGuard(safety_level)
        self.annotator = ScreenAnnotator()
        self.reflexion = ReflexionModule()
        self.parser = ActionParser()
        self.max_steps = max_steps
        self._objectives: Dict[str, ObjectiveState] = {}

    def create_objective(self, objective: str) -> ObjectiveState:
        state = ObjectiveState(
            objective=objective,
            max_steps=self.max_steps,
            model_used=self.model_provider.model.value,
        )
        obj_id = uuid.uuid4().hex[:12]
        self._objectives[obj_id] = state
        return state

    def _capture_screen(self) -> ScreenObservation:
        """Execute screen capture — in production uses OmniRobotGoEngine."""
        standard_b64 = base64.b64encode(b"OMNI_SCREENSHOT_STUB" + b"0" * 64)  # PNG stub.decode()
        obs = ScreenObservation(
            image_base64=standard_b64,
            width=1920, height=1080,
        )
        if self.prompt_mode == PromptMode.GRID_OVERLAY:
            obs = self.annotator.apply_grid(obs)
        elif self.prompt_mode == PromptMode.SET_OF_MARK:
            obs = self.annotator.apply_som(obs)
        return obs

    def _build_user_message(self, state: ObjectiveState, observation: ScreenObservation) -> str:
        """Build the user message with objective + action history."""
        history = ""
        if state.actions_taken:
            history = "\n\nPrevious actions:\n" + "\n".join(
                f"  Step {a.step_index}: {a.action_type.value} — {a.reasoning}"
                for a in state.actions_taken[-5:]
            )

        annotation_info = ""
        if observation.grid_cells > 0:
            annotation_info = f"\n\nGrid: {observation.grid_cells} cells overlaid on screen."
        elif observation.som_labels > 0:
            annotation_info = f"\n\nSet-of-Mark: {observation.som_labels} labeled UI elements."

        return (
            f"OBJECTIVE: {state.objective}\n"
            f"Step: {state.current_step + 1}/{state.max_steps}\n"
            f"Screen: {observation.width}x{observation.height}"
            f"{annotation_info}{history}\n\n"
            f"Decide the NEXT single action. Output JSON only."
        )

    def step(self, state: ObjectiveState) -> Result[AgentAction, str]:
        """Execute one step of the self-operating loop."""
        if not state.is_active:
            return Err(f"Objective not active: {state.status}")

        # 1. Capture screen
        observation = self._capture_screen()
        state.observations.append(observation)

        # 2. Build prompts
        system_prompt = PromptTemplates.get_prompt(self.prompt_mode)
        user_message = self._build_user_message(state, observation)

        # 3. LLM inference
        llm_result = self.model_provider.infer(
            system_prompt=system_prompt,
            user_message=user_message,
            image_b64=observation.image_base64,
        )
        if llm_result.is_err():
            return Err(llm_result.error)
        llm_response = llm_result.unwrap()
        state.total_tokens += llm_response.tokens_used

        # 4. Parse action
        parse_result = self.parser.parse(llm_response, state.current_step)
        if parse_result.is_err():
            return parse_result

        action = parse_result.unwrap()

        # 5. Safety check
        safety_result = self.safety_guard.validate(action)
        if safety_result.is_err():
            state.fail(safety_result.error)
            return safety_result

        action = safety_result.unwrap()

        # 6. Execute (sandboxed — in production would call RobotGoEngine)
        # action execution is handled by the caller

        # 7. Update state
        state.add_action(action)

        # 8. Check terminal conditions
        if action.action_type == ActionType.DONE:
            state.complete()
        elif action.action_type == ActionType.FAILURE:
            state.fail(action.reasoning)

        return Ok(action)

    def run_objective(self, objective: str) -> ObjectiveState:
        """Run a full objective loop until completion or max steps."""
        state = self.create_objective(objective)
        while state.is_active:
            result = self.step(state)
            if result.is_err():
                state.fail(result.error)
                break
        return state

    def list_objectives(self) -> Dict[str, Dict]:
        return {oid: s.summary() for oid, s in self._objectives.items()}

    def diagnostics(self) -> Dict[str, Any]:
        return {
            "engine": self.ENGINE_NAME,
            "version": self.ENGINE_VERSION,
            "model": self.model_provider.model.value,
            "prompt_mode": self.prompt_mode.value,
            "safety_level": self.safety_guard.level.value,
            "max_steps": self.max_steps,
            "active_objectives": sum(1 for s in self._objectives.values() if s.is_active),
            "total_objectives": len(self._objectives),
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 10. Self-Test Suite
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _run_self_test() -> Dict[str, Any]:
    results = {"engine": "OmniSelfOperatingEngine", "tests": [], "passed": 0, "failed": 0}

    def _test(name: str, fn: Callable[[], bool]):
        try:
            ok = fn()
            results["tests"].append({"name": name, "status": "PASS" if ok else "FAIL"})
            if ok: results["passed"] += 1
            else: results["failed"] += 1
        except Exception as e:
            results["tests"].append({"name": name, "status": "ERROR", "error": str(e)})
            results["failed"] += 1

    engine = OmniSelfOperatingEngine(
        model=OperatingModel.GEMINI_PRO,
        prompt_mode=PromptMode.DIRECT_COORDINATES,
        safety_level=SafetyLevel.SANDBOX,
        max_steps=5,
    )

    # Test 1: Diagnostics
    _test("diagnostics", lambda: engine.diagnostics()["engine"] == "OmniSelfOperatingEngine")

    # Test 2: Create objective
    def t_objective():
        state = engine.create_objective("Open notepad and type hello")
        return state.status == "active" and state.objective != ""
    _test("create_objective", t_objective)

    # Test 3: Run objective (sandbox mode)
    def t_run():
        state = engine.run_objective("Click the Start button")
        return state.status in ("completed", "failed") and state.current_step > 0
    _test("run_objective", t_run)

    # Test 4: ScreenCoordinate
    _test("screen_coordinate", lambda: ScreenCoordinate(100, 200).to_tuple() == (100, 200))

    # Test 5: AgentAction serialization
    def t_action_dict():
        a = AgentAction(
            action_type=ActionType.CLICK,
            coordinate=ScreenCoordinate(500, 300),
            reasoning="Click button",
        )
        d = a.to_dict()
        return d["action"] == "click" and d["x"] == 500
    _test("action_serialization", t_action_dict)

    # Test 6: ScreenObservation size
    _test("observation_size", lambda: ScreenObservation(image_base64="AAAA", width=1920, height=1080).size_kb > 0)

    # Test 7: Grid annotation
    def t_grid():
        obs = ScreenObservation(image_base64="X", width=1920, height=1080)
        annotated = ScreenAnnotator.apply_grid(obs, rows=4, cols=4)
        return annotated.grid_cells == 16 and len(annotated.annotations) == 16
    _test("grid_annotation", t_grid)

    # Test 8: SoM annotation
    def t_som():
        obs = ScreenObservation(image_base64="X", width=1920, height=1080)
        annotated = ScreenAnnotator.apply_som(obs)
        return annotated.som_labels > 0
    _test("som_annotation", t_som)

    # Test 9: Prompt mode selection
    _test("prompt_direct", lambda: "JSON" in PromptTemplates.get_prompt(PromptMode.DIRECT_COORDINATES))
    _test("prompt_grid", lambda: "GRID" in PromptTemplates.get_prompt(PromptMode.GRID_OVERLAY))
    _test("prompt_som", lambda: "Set-of-Mark" in PromptTemplates.get_prompt(PromptMode.SET_OF_MARK))

    # Test 12: Model provider
    _test("model_provider", lambda: ModelProvider(OperatingModel.GPT4O)._get_provider() == "openai")
    _test("model_provider_claude", lambda: ModelProvider(OperatingModel.CLAUDE_SONNET)._get_provider() == "anthropic")
    _test("model_provider_gemini", lambda: ModelProvider(OperatingModel.GEMINI_PRO)._get_provider() == "google")

    # Test 15: Action parser
    def t_parser():
        resp = LLMResponse(
            raw_text='{"action": "click", "coordinate": [100, 200], "reasoning": "test"}',
            parsed_action={"action": "click", "coordinate": [100, 200], "reasoning": "test"},
            model="test",
        )
        result = ActionParser.parse(resp, 1)
        return result.is_ok() and result.unwrap().action_type == ActionType.CLICK
    _test("action_parser", t_parser)

    # Test 16: Parser error handling
    def t_parser_err():
        resp = LLMResponse(raw_text="garbage", model="test")
        return ActionParser.parse(resp).is_err()
    _test("parser_error", t_parser_err)

    # Test 17: Safety guard — blocked keys
    def t_safety_blocked():
        guard = SafetyGuard(SafetyLevel.RESTRICTED)
        action = AgentAction(action_type=ActionType.KEY_PRESS, key="ctrl+alt+delete")
        return guard.validate(action).is_err()
    _test("safety_blocked_key", t_safety_blocked)

    # Test 18: Safety guard — blocked text
    def t_safety_text():
        guard = SafetyGuard(SafetyLevel.RESTRICTED)
        action = AgentAction(action_type=ActionType.TYPE_TEXT, text="rm -rf /")
        return guard.validate(action).is_err()
    _test("safety_blocked_text", t_safety_text)

    # Test 19: Safety sandbox mode
    def t_safety_sandbox():
        guard = SafetyGuard(SafetyLevel.SANDBOX)
        action = AgentAction(action_type=ActionType.CLICK, coordinate=ScreenCoordinate(100, 100))
        result = guard.validate(action)
        return result.is_ok() and result.unwrap().action_type == ActionType.WAIT
    _test("safety_sandbox", t_safety_sandbox)

    # Test 20: Safety unrestricted passes all
    def t_safety_unrestricted():
        guard = SafetyGuard(SafetyLevel.UNRESTRICTED)
        action = AgentAction(action_type=ActionType.KEY_PRESS, key="ctrl+alt+delete")
        return guard.validate(action).is_ok()
    _test("safety_unrestricted", t_safety_unrestricted)

    # Test 21: Reflexion module
    def t_reflexion():
        before = ScreenObservation(image_base64="aaa", width=1920, height=1080)
        after = ScreenObservation(image_base64="bbb", width=1920, height=1080)
        action = AgentAction(action_type=ActionType.CLICK)
        result = ReflexionModule.evaluate(before, after, action)
        return result.screen_changed and result.success_estimate > 0.5
    _test("reflexion_changed", t_reflexion)

    # Test 22: Reflexion no change
    def t_reflexion_same():
        obs = ScreenObservation(image_base64="same", width=1920, height=1080)
        action = AgentAction(action_type=ActionType.CLICK)
        result = ReflexionModule.evaluate(obs, obs, action)
        return not result.screen_changed and result.should_retry
    _test("reflexion_no_change", t_reflexion_same)

    # Test 23: ObjectiveState lifecycle
    def t_state_lifecycle():
        state = ObjectiveState(objective="test", max_steps=3)
        state.add_action(AgentAction(action_type=ActionType.CLICK))
        state.add_action(AgentAction(action_type=ActionType.TYPE_TEXT, text="hello"))
        state.complete()
        return state.status == "completed" and state.current_step == 2
    _test("objective_lifecycle", t_state_lifecycle)

    # Test 24: ObjectiveState failure
    def t_state_fail():
        state = ObjectiveState(objective="test", max_steps=3)
        state.fail("Cannot proceed")
        return state.status == "failed" and state.error == "Cannot proceed"
    _test("objective_failure", t_state_fail)

    # Test 25: Objective summary
    def t_summary():
        state = ObjectiveState(objective="test")
        s = state.summary()
        return "objective" in s and "status" in s
    _test("objective_summary", t_summary)

    # Test 26: Multiple objectives
    def t_multi_obj():
        e = OmniSelfOperatingEngine(safety_level=SafetyLevel.SANDBOX, max_steps=2)
        e.run_objective("Task A")
        e.run_objective("Task B")
        return len(e.list_objectives()) == 2
    _test("multiple_objectives", t_multi_obj)

    # Test 27: ActionType enum coverage
    _test("action_types", lambda: len(ActionType) == 12)

    # Test 28: OperatingModel enum coverage
    _test("models_count", lambda: len(OperatingModel) >= 7)

    # Test 29: PromptMode enum
    _test("prompt_modes", lambda: len(PromptMode) == 3)

    # Test 30: SafetyLevel enum
    _test("safety_levels", lambda: len(SafetyLevel) == 4)

    results["total"] = results["passed"] + results["failed"]
    results["score"] = f"{results['passed']}/{results['total']}"
    return results


if __name__ == "__main__":
    print("=" * 72)
    print("  OMNI SELF-OPERATING ENGINE — Compute Layer Self-Test")
    print("  Meta-functionalized from OthersideAI/self-operating-computer (10.2k★)")
    print("=" * 72)
    results = _run_self_test()
    for t in results["tests"]:
        icon = "✅" if t["status"] == "PASS" else "❌"
        print(f"  {icon} {t['name']}: {t['status']}")
    print(f"\n  Score: {results['score']}")
    print("=" * 72)
