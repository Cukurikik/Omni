ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI OPEN INTERFACE ENGINE — AI-Powered Desktop Computer Control
# ===========================================================================
# Source Paradigm: https://github.com/AmberSahdev/Open-Interface
# Domain Layer  : AI Agents (Computer Control)
# Zero-Prod     : 100% Native — ctypes, subprocess, os, json
# ===========================================================================
"""
Open-Interface teaches us:
  1. Natural language → computer action translation
  2. Screenshot-based screen observation for course correction
  3. Mouse/keyboard execute for task execution
  4. Cross-platform input control (Windows/Mac/Linux)
  5. Step-by-step task decomposition
  6. Error recovery via visual feedback loop

This engine distills those paradigms into OMNI-native Python for
programmatic desktop control using ctypes (Win32) and subprocess.
"""

import ctypes
import json
import os
import subprocess
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class ScreenInfo:
    width: int = 0
    height: int = 0
    dpi: int = 96
    monitors: int = 1


@dataclass
class MousePosition:
    x: int = 0
    y: int = 0


@dataclass
class ActionStep:
    action: str         # "click", "type", "key", "scroll", "screenshot", "wait", "shell"
    params: Dict = field(default_factory=dict)
    description: str = ""
    status: str = "pending"
    result: Dict = field(default_factory=dict)
    duration_ms: float = 0


# ── Screen Controller (Windows ctypes) ─────────────────────────────────────

class ScreenController:
    """Native screen information and control."""

    @staticmethod
    def get_screen_info() -> ScreenInfo:
        if os.name != "nt":
            return ScreenInfo()
        try:
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            return ScreenInfo(
                width=user32.GetSystemMetrics(0),
                height=user32.GetSystemMetrics(1),
                dpi=user32.GetDpiForSystem() if hasattr(user32, 'GetDpiForSystem') else 96,
                monitors=user32.GetSystemMetrics(80),
            )
        except Exception:
            return ScreenInfo()

    @staticmethod
    def get_cursor_pos() -> MousePosition:
        if os.name != "nt":
            return MousePosition()
        try:
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            pt = POINT()
            ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
            return MousePosition(x=pt.x, y=pt.y)
        except Exception:
            return MousePosition()

    @staticmethod
    def set_cursor_pos(x: int, y: int) -> bool:
        if os.name != "nt":
            return False
        try:
            ctypes.windll.user32.SetCursorPos(x, y)
            return True
        except Exception:
            return False

    @staticmethod
    def click(x: int, y: int, button: str = "left") -> bool:
        """Move cursor and click at position."""
        if os.name != "nt":
            return False
        try:
            ctypes.windll.user32.SetCursorPos(x, y)
            time.sleep(0.05)
            if button == "left":
                ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # LEFTDOWN
                ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # LEFTUP
            elif button == "right":
                ctypes.windll.user32.mouse_event(0x0008, 0, 0, 0, 0)  # RIGHTDOWN
                ctypes.windll.user32.mouse_event(0x0010, 0, 0, 0, 0)  # RIGHTUP
            return True
        except Exception:
            return False

    @staticmethod
    def double_click(x: int, y: int) -> bool:
        ScreenController.click(x, y)
        time.sleep(0.05)
        return ScreenController.click(x, y)

    @staticmethod
    def scroll(amount: int) -> bool:
        """Scroll mouse wheel. Positive = up, negative = down."""
        if os.name != "nt":
            return False
        try:
            MOUSEEVENTF_WHEEL = 0x0800
            ctypes.windll.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, amount * 120, 0)
            return True
        except Exception:
            return False


# ── Keyboard Controller ────────────────────────────────────────────────────

class KeyboardController:
    """Native keyboard input execute."""

    KEYMAP = {
        "enter": 0x0D, "tab": 0x09, "escape": 0x1B, "space": 0x20,
        "backspace": 0x08, "delete": 0x2E, "home": 0x24, "end": 0x23,
        "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
        "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73, "f5": 0x74,
        "ctrl": 0x11, "alt": 0x12, "shift": 0x10, "win": 0x5B,
    }

    @staticmethod
    def press_key(key: str) -> bool:
        if os.name != "nt":
            return False
        try:
            vk = KeyboardController.KEYMAP.get(key.lower())
            if vk:
                ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
                ctypes.windll.user32.keybd_event(vk, 0, 2, 0)  # KEYUP
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def hotkey(*keys: str) -> bool:
        """Press a combination of keys (e.g., ctrl+c)."""
        if os.name != "nt":
            return False
        try:
            vk_codes = []
            for k in keys:
                vk = KeyboardController.KEYMAP.get(k.lower())
                if vk:
                    vk_codes.append(vk)
            for vk in vk_codes:
                ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
            for vk in reversed(vk_codes):
                ctypes.windll.user32.keybd_event(vk, 0, 2, 0)
            return True
        except Exception:
            return False

    @staticmethod
    def type_text_via_powershell(text: str) -> Dict:
        """Type text using PowerShell SendKeys (safer for complex text)."""
        if os.name != "nt":
            return {"error": "Windows only"}
        safe = text.replace("'", "''")
        try:
            r = subprocess.run(
                ["powershell", "-Command",
                 f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{safe}')"],
                capture_output=True, text=True, timeout=10,
            )
            return {"typed": r.returncode == 0, "text_length": len(text)}
        except Exception as e:
            return {"error": str(e)[:256]}


# ── Screenshot Capture ─────────────────────────────────────────────────────

class ScreenCapture:
    """Capture screenshots for visual feedback."""

    @staticmethod
    def capture(output_path: str) -> Dict:
        """Take a screenshot using PowerShell."""
        if os.name != "nt":
            return {"error": "Windows only"}
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
$screen = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap($screen.Width, $screen.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($screen.Location, [System.Drawing.Point]::Empty, $screen.Size)
$bmp.Save('{output_path}')
$g.Dispose()
$bmp.Dispose()
"""
        try:
            r = subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True, text=True, timeout=10,
            )
            if os.path.isfile(output_path):
                return {"saved": output_path, "size_kb": round(os.path.getsize(output_path) / 1024, 2)}
            return {"error": r.stderr[:256]}
        except Exception as e:
            return {"error": str(e)[:256]}


# ── Action Executor ────────────────────────────────────────────────────────

class ActionExecutor:
    """Execute desktop control actions."""

    def __init__(self):
        self.screen = ScreenController()
        self.keyboard = KeyboardController()
        self.capture = ScreenCapture()

    def execute(self, step: ActionStep) -> Dict:
        start = time.perf_counter()
        result = {}

        if step.action == "click":
            ok = self.screen.click(step.params.get("x", 0), step.params.get("y", 0),
                                    step.params.get("button", "left"))
            result = {"clicked": ok}

        elif step.action == "double_click":
            ok = self.screen.double_click(step.params.get("x", 0), step.params.get("y", 0))
            result = {"double_clicked": ok}

        elif step.action == "type":
            result = self.keyboard.type_text_via_powershell(step.params.get("text", ""))

        elif step.action == "key":
            ok = self.keyboard.press_key(step.params.get("key", ""))
            result = {"pressed": ok}

        elif step.action == "hotkey":
            keys = step.params.get("keys", [])
            ok = self.keyboard.hotkey(*keys)
            result = {"hotkey": ok}

        elif step.action == "scroll":
            ok = self.screen.scroll(step.params.get("amount", -3))
            result = {"scrolled": ok}

        elif step.action == "screenshot":
            path = step.params.get("path", "screenshot.png")
            result = self.capture.capture(path)

        elif step.action == "wait":
            secs = min(step.params.get("seconds", 1), 30)
            time.sleep(secs)
            result = {"waited": secs}

        elif step.action == "shell":
            cmd = step.params.get("command", "")
            try:
                r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                result = {"exit_code": r.returncode, "stdout": r.stdout[:2048]}
            except Exception as e:
                result = {"error": str(e)[:256]}

        step.duration_ms = round((time.perf_counter() - start) * 1000, 2)
        step.result = result
        step.status = "completed"
        return result


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniOpenInterfaceEngine:
    """
    OMNI Open Interface Engine — Zero-Prod AI Desktop Computer Control.

    Capabilities (all native ctypes + subprocess):
      - Mouse click/double-click/scroll at coordinates
      - Keyboard key press and hotkey combos
      - Text typing via PowerShell SendKeys
      - Screenshot capture for visual feedback
      - Screen info (resolution, DPI, monitors)
      - Shell command execution
    """

    def __init__(self):
        self.executor = ActionExecutor()
        self.screen_ctrl = ScreenController()

    def get_screen(self) -> Dict:
        info = self.screen_ctrl.get_screen_info()
        return {"width": info.width, "height": info.height,
                "dpi": info.dpi, "monitors": info.monitors}

    def get_cursor(self) -> Dict:
        pos = self.screen_ctrl.get_cursor_pos()
        return {"x": pos.x, "y": pos.y}

    def execute_steps(self, steps: List[Dict]) -> List[Dict]:
        results = []
        for cfg in steps:
            step = ActionStep(
                action=cfg.get("action", ""),
                params=cfg.get("params", {}),
                description=cfg.get("description", ""),
            )
            self.executor.execute(step)
            results.append({
                "action": step.action, "status": step.status,
                "result": step.result, "ms": step.duration_ms,
            })
        return results

    def diagnostics(self) -> Dict:
        screen = self.screen_ctrl.get_screen_info()
        cursor = self.screen_ctrl.get_cursor_pos()
        return {
            "engine": "OmniOpenInterfaceEngine",
            "status": "active",
            "platform": os.name,
            "screen": {"w": screen.width, "h": screen.height, "dpi": screen.dpi},
            "cursor": {"x": cursor.x, "y": cursor.y},
            "capabilities": ["mouse_click", "double_click", "scroll",
                             "key_press", "hotkey", "type_text",
                             "screenshot", "shell_exec", "screen_info"],
        }


if __name__ == "__main__":
    engine = OmniOpenInterfaceEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
