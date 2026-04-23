ENGINE_VERSION = "1.0.0-omni"
# ===========================================================================
# OMNI ANDROID VIEW CLIENT ENGINE — Android UI Inspection & Testing
# ===========================================================================
# Source Paradigm: https://github.com/dtmilano/AndroidViewClient
# Domain Layer  : Mobile (Android UI Automation)
# Zero-Prod     : 100% Native — subprocess (ADB), re, json, os
# ===========================================================================
"""
AndroidViewClient teaches us:
  1. View hierarchy dumping via ADB (uiautomator dump)
  2. View property inspection (bounds, text, class, resource-id)
  3. Touch/click by view ID or text
  4. Screenshot with view overlay
  5. View tree traversal and search
  6. Accessibility testing

This engine distills those paradigms into OMNI-native Python for
Android UI hierarchy inspection and element interaction via ADB.
"""

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ── Data Models ──────────────────────────────────────────────────────────────

@dataclass
class ViewNode:
    resource_id: str = ""
    class_name: str = ""
    text: str = ""
    content_desc: str = ""
    bounds: Tuple[int, int, int, int] = (0, 0, 0, 0)
    clickable: bool = False
    enabled: bool = True
    focused: bool = False
    checkable: bool = False
    checked: bool = False
    children: int = 0


# ── ADB UI Dumper ──────────────────────────────────────────────────────────

class ADBUIDumper:
    """Dump and parse Android UI hierarchy via ADB."""

    @staticmethod
    def check_adb() -> Dict:
        try:
            r = subprocess.run(["adb", "version"], capture_output=True, text=True, timeout=5)
            return {"installed": r.returncode == 0, "version": r.stdout.strip().split("\n")[0]}
        except FileNotFoundError:
            return {"installed": False, "version": ""}

    @staticmethod
    def get_devices() -> List[str]:
        try:
            r = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
            devices = []
            for line in r.stdout.strip().split("\n")[1:]:
                parts = line.split("\t")
                if len(parts) >= 2 and parts[1].strip() in ("device", "online"):
                    devices.append(parts[0].strip())
            return devices
        except FileNotFoundError:
            return []

    @staticmethod
    def dump_hierarchy(serial: str = "") -> str:
        """Dump UI hierarchy XML."""
        args = ["adb"]
        if serial:
            args.extend(["-s", serial])
        args.extend(["shell", "uiautomator", "dump", "/dev/tty"])
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=15)
            return r.stdout
        except Exception:
            return ""

    @staticmethod
    def parse_views(xml_content: str) -> List[ViewNode]:
        """Parse view nodes from UI hierarchy XML."""
        views = []
        pattern = re.compile(
            r'<node\s+'
            r'.*?resource-id="([^"]*)"'
            r'.*?class="([^"]*)"'
            r'.*?text="([^"]*)"'
            r'.*?content-desc="([^"]*)"'
            r'.*?clickable="([^"]*)"'
            r'.*?enabled="([^"]*)"'
            r'.*?bounds="\[(\d+),(\d+)\]\[(\d+),(\d+)\]"',
            re.DOTALL,
        )
        for m in pattern.finditer(xml_content):
            views.append(ViewNode(
                resource_id=m.group(1),
                class_name=m.group(2),
                text=m.group(3),
                content_desc=m.group(4),
                clickable=m.group(5) == "true",
                enabled=m.group(6) == "true",
                bounds=(int(m.group(7)), int(m.group(8)), int(m.group(9)), int(m.group(10))),
            ))
        return views

    @staticmethod
    def find_by_text(views: List[ViewNode], text: str) -> List[ViewNode]:
        return [v for v in views if text.lower() in v.text.lower()]

    @staticmethod
    def find_by_id(views: List[ViewNode], resource_id: str) -> List[ViewNode]:
        return [v for v in views if resource_id in v.resource_id]

    @staticmethod
    def find_clickable(views: List[ViewNode]) -> List[ViewNode]:
        return [v for v in views if v.clickable]


# ── UI Interactor ──────────────────────────────────────────────────────────

class UIInteractor:
    """Interact with Android UI elements via ADB."""

    @staticmethod
    def _shell(serial: str, cmd: str) -> Dict:
        args = ["adb"]
        if serial:
            args.extend(["-s", serial])
        args.extend(["shell", cmd])
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=10)
            return {"exit_code": r.returncode, "stdout": r.stdout[:4096]}
        except Exception as e:
            return {"error": str(e)[:256]}

    @staticmethod
    def tap_view(serial: str, view: ViewNode) -> Dict:
        """Tap the center of a view's bounds."""
        cx = (view.bounds[0] + view.bounds[2]) // 2
        cy = (view.bounds[1] + view.bounds[3]) // 2
        return UIInteractor._shell(serial, f"input tap {cx} {cy}")

    @staticmethod
    def type_in_view(serial: str, view: ViewNode, text: str) -> Dict:
        """Tap a view and type text."""
        UIInteractor.tap_view(serial, view)
        time.sleep(0.3)
        safe = text.replace(" ", "%s").replace("'", "\\'")
        return UIInteractor._shell(serial, f"input text '{safe}'")

    @staticmethod
    def get_current_activity(serial: str = "") -> Dict:
        args = ["adb"]
        if serial:
            args.extend(["-s", serial])
        args.extend(["shell", "dumpsys", "activity", "activities"])
        try:
            r = subprocess.run(args, capture_output=True, text=True, timeout=10)
            m = re.search(r'mResumedActivity.*?(\S+/\S+)', r.stdout)
            return {"current_activity": m.group(1) if m else "unknown"}
        except Exception as e:
            return {"error": str(e)[:256]}

    @staticmethod
    def take_screenshot(serial: str, output_path: str) -> Dict:
        remote = "/sdcard/omni_avc_screenshot.png"
        args = ["adb"]
        if serial:
            args.extend(["-s", serial])
        try:
            subprocess.run(args + ["shell", f"screencap -p {remote}"],
                           capture_output=True, timeout=10)
            r = subprocess.run(args + ["pull", remote, output_path],
                               capture_output=True, text=True, timeout=10)
            return {"saved": output_path if r.returncode == 0 else "",
                    "error": r.stderr[:256] if r.returncode != 0 else ""}
        except Exception as e:
            return {"error": str(e)[:256]}


# ── The Main Engine ─────────────────────────────────────────────────────────

class OmniAndroidViewClientEngine:
    """
    OMNI AndroidViewClient Engine — Zero-Prod Android UI Inspection.

    Capabilities (all native ADB subprocess):
      - UI hierarchy dump and XML parsing
      - View search by text, resource-id, clickability
      - Element tap and text input
      - Current activity detection
      - Screenshot capture
    """

    def __init__(self):
        self.dumper = ADBUIDumper()
        self.interactor = UIInteractor()

    def list_devices(self) -> List[str]:
        return self.dumper.get_devices()

    def dump_views(self, serial: str = "") -> Dict:
        xml = self.dumper.dump_hierarchy(serial)
        views = self.dumper.parse_views(xml)
        return {
            "total_views": len(views),
            "clickable": len(self.dumper.find_clickable(views)),
            "views": [{"id": v.resource_id, "text": v.text[:50],
                       "class": v.class_name.split(".")[-1],
                       "clickable": v.clickable} for v in views[:20]],
        }

    def diagnostics(self) -> Dict:
        adb = self.dumper.check_adb()
        devices = self.dumper.get_devices()
        return {
            "engine": "OmniAndroidViewClientEngine",
            "status": "active",
            "adb": adb,
            "devices": len(devices),
            "capabilities": ["ui_dump", "view_parse", "find_by_text",
                             "find_by_id", "tap_view", "type_text",
                             "current_activity", "screenshot"],
        }


if __name__ == "__main__":
    engine = OmniAndroidViewClientEngine()
    print(json.dumps(engine.diagnostics(), indent=2))
