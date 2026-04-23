"""
OMNI Shortcuts Builder Engine
===============================
Production-grade iOS/Apple Shortcuts builder engine inspired by
a2/swift-shortcuts. Programmatic creation of Shortcuts workflows
using a Python DSL, exported as importable .shortcut plist files.

Source Reference: https://github.com/a2/swift-shortcuts
OMNI Layer: compute (Python)
"""

from __future__ import annotations

import hashlib
import json
import os
import plistlib
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union


ENGINE_VERSION = "1.0.0"


# ============================================================================
# 1. Action Types & Identifiers
# ============================================================================
from src.compute.python_core.omni_base_engine import Result, Ok, Err

class ActionID(Enum):
    """Standard iOS Shortcuts action identifiers."""
    COMMENT = "is.workflow.actions.comment"
    SHOW_RESULT = "is.workflow.actions.showresult"
    SHOW_ALERT = "is.workflow.actions.alert"
    ASK_FOR_INPUT = "is.workflow.actions.ask"
    SET_VARIABLE = "is.workflow.actions.setvariable"
    GET_VARIABLE = "is.workflow.actions.getvariable"
    TEXT = "is.workflow.actions.gettext"
    NUMBER = "is.workflow.actions.number"
    CALCULATE = "is.workflow.actions.math"
    COUNT = "is.workflow.actions.count"
    LIST = "is.workflow.actions.list"
    CHOOSE_FROM_LIST = "is.workflow.actions.choosefromlist"
    CHOOSE_FROM_MENU = "is.workflow.actions.choosefrommenu"
    IF = "is.workflow.actions.conditional"
    REPEAT = "is.workflow.actions.repeat.count"
    REPEAT_EACH = "is.workflow.actions.repeat.each"
    NOTHING = "is.workflow.actions.nothing"
    WAIT = "is.workflow.actions.delay"
    # Web
    GET_URL = "is.workflow.actions.downloadurl"
    OPEN_URL = "is.workflow.actions.openurl"
    URL = "is.workflow.actions.url"
    URL_ENCODE = "is.workflow.actions.urlencode"
    GET_URLS_FROM_INPUT = "is.workflow.actions.detect.link"
    # Text
    REPLACE_TEXT = "is.workflow.actions.text.replace"
    MATCH_TEXT = "is.workflow.actions.text.match"
    CHANGE_CASE = "is.workflow.actions.text.changecase"
    SPLIT_TEXT = "is.workflow.actions.text.split"
    COMBINE_TEXT = "is.workflow.actions.text.combine"
    # Media
    TAKE_PHOTO = "is.workflow.actions.takephoto"
    SELECT_PHOTOS = "is.workflow.actions.selectphoto"
    # Device
    SET_BRIGHTNESS = "is.workflow.actions.setbrightness"
    SET_VOLUME = "is.workflow.actions.setvolume"
    SET_WIFI = "is.workflow.actions.wifi.set"
    SET_BLUETOOTH = "is.workflow.actions.bluetooth.set"
    SET_LOW_POWER_MODE = "is.workflow.actions.lowpowermode.set"
    GET_BATTERY_LEVEL = "is.workflow.actions.getbatterylevel"
    VIBRATE = "is.workflow.actions.vibrate"
    # Clipboard
    COPY_TO_CLIPBOARD = "is.workflow.actions.setclipboard"
    GET_CLIPBOARD = "is.workflow.actions.getclipboard"
    # Share
    SHARE = "is.workflow.actions.share"
    # Notifications
    SHOW_NOTIFICATION = "is.workflow.actions.notification"
    # Date/Time
    GET_DATE = "is.workflow.actions.date"
    FORMAT_DATE = "is.workflow.actions.format.date"
    # Files
    GET_FILE = "is.workflow.actions.documentpicker.open"
    SAVE_FILE = "is.workflow.actions.documentpicker.save"
    # Dictionary
    DICTIONARY = "is.workflow.actions.dictionary"
    GET_DICT_VALUE = "is.workflow.actions.getvalueforkey"
    SET_DICT_VALUE = "is.workflow.actions.setvalueforkey"
    # HTTP
    GET_CONTENTS_OF_URL = "is.workflow.actions.downloadurl"
    # Scripting
    RUN_SHORTCUT = "is.workflow.actions.runworkflow"
    RUN_JAVASCRIPT = "is.workflow.actions.runjavascriptonwebpage"
    # Output
    SET_OUTPUT = "is.workflow.actions.output"


# ============================================================================
# 2. Core Action Building Blocks
# ============================================================================

@dataclass
class ShortcutAction:
    """A single action in a shortcut workflow."""
    identifier: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    group_id: str = ""
    group_mode: str = ""  # "has-body" for control flow start

    def to_plist_dict(self) -> Dict[str, Any]:
        """Convert to plist dict representation."""
        result: Dict[str, Any] = {
            "WFWorkflowActionIdentifier": self.identifier,
            "WFWorkflowActionParameters": dict(self.parameters),
        }
        if self.group_id:
            result["WFWorkflowActionParameters"]["GroupingIdentifier"] = self.group_id
            if self.group_mode:
                result["WFWorkflowActionParameters"]["WFControlFlowMode"] = (
                    0 if self.group_mode == "start" else
                    1 if self.group_mode == "middle" else 2
                )
        return result


class ActionBuilder:
    """Fluent builder for creating shortcut actions."""

    @staticmethod
    def comment(text: str) -> ShortcutAction:
        """Execute comment operation for ActionBuilder."""
        return ShortcutAction(
            identifier=ActionID.COMMENT.value,
            parameters={"WFCommentActionText": text},
        )

    @staticmethod
    def show_result(text: str) -> ShortcutAction:
        """Execute show result operation for ActionBuilder."""
        return ShortcutAction(
            identifier=ActionID.SHOW_RESULT.value,
            parameters={"Text": _text_token(text)},
        )

    @staticmethod
    def show_alert(title: str, message: str = "",
                   show_cancel: bool = True) -> ShortcutAction:
        """Execute show alert operation for ActionBuilder."""
        params: Dict[str, Any] = {"WFAlertActionTitle": title}
        if message:
            params["WFAlertActionMessage"] = message
        if not show_cancel:
            params["WFAlertActionCancelButtonShown"] = False
        return ShortcutAction(identifier=ActionID.SHOW_ALERT.value, parameters=params)

    @staticmethod
    def ask_for_input(prompt: str = "", input_type: str = "Text",
                      default: str = "") -> ShortcutAction:
        """Execute ask for input operation for ActionBuilder."""
        params: Dict[str, Any] = {}
        if prompt:
            params["WFAskActionPrompt"] = prompt
        if default:
            params["WFAskActionDefaultAnswer"] = default
        return ShortcutAction(identifier=ActionID.ASK_FOR_INPUT.value, parameters=params)

    @staticmethod
    def text(content: str) -> ShortcutAction:
        """Execute text operation for ActionBuilder."""
        return ShortcutAction(
            identifier=ActionID.TEXT.value,
            parameters={"WFTextActionText": _text_token(content)},
        )

    @staticmethod
    def number(value: float) -> ShortcutAction:
        """Execute number operation for ActionBuilder."""
        return ShortcutAction(
            identifier=ActionID.NUMBER.value,
            parameters={"WFNumberActionNumber": value},
        )

    @staticmethod
    def get_url(url: str, method: str = "GET",
                headers: Optional[Dict[str, str]] = None,
                body: Optional[Dict[str, str]] = None) -> ShortcutAction:
        """Retrieve url from ActionBuilder."""
        params: Dict[str, Any] = {"WFURL": url}
        if method != "GET":
            params["WFHTTPMethod"] = method
        if headers:
            params["WFHTTPHeaders"] = {
                "Value": {
                    "WFDictionaryFieldValueItems": [
                        {"WFItemType": 0, "WFKey": k, "WFValue": v}
                        for k, v in headers.items()
                    ]
                }
            }
        if body:
            params["WFHTTPBodyType"] = "Form"
            params["WFFormValues"] = {
                "Value": {
                    "WFDictionaryFieldValueItems": [
                        {"WFItemType": 0, "WFKey": k, "WFValue": v}
                        for k, v in body.items()
                    ]
                }
            }
        return ShortcutAction(identifier=ActionID.GET_CONTENTS_OF_URL.value, parameters=params)

    @staticmethod
    def open_url(url: str) -> ShortcutAction:
        """Execute open url operation for ActionBuilder."""
        return ShortcutAction(
            identifier=ActionID.OPEN_URL.value,
            parameters={"WFInput": _text_token(url)},
        )

    @staticmethod
    def set_variable(name: str) -> ShortcutAction:
        """Set variable for ActionBuilder."""
        return ShortcutAction(
            identifier=ActionID.SET_VARIABLE.value,
            parameters={"WFVariableName": name},
        )

    @staticmethod
    def get_variable(name: str) -> ShortcutAction:
        """Retrieve variable from ActionBuilder."""
        return ShortcutAction(
            identifier=ActionID.GET_VARIABLE.value,
            parameters={"WFVariable": {"Value": {"VariableName": name}, "Type": "Variable"}},
        )

    @staticmethod
    def wait(seconds: float) -> ShortcutAction:
        """Execute wait operation for ActionBuilder."""
        return ShortcutAction(
            identifier=ActionID.WAIT.value,
            parameters={"WFDelayTime": seconds},
        )

    @staticmethod
    def battery_level() -> ShortcutAction:
        """Execute battery level operation for ActionBuilder."""
        return ShortcutAction(identifier=ActionID.GET_BATTERY_LEVEL.value)

    @staticmethod
    def set_low_power_mode(enabled: bool = True) -> ShortcutAction:
        """Set low power mode for ActionBuilder."""
        return ShortcutAction(
            identifier=ActionID.SET_LOW_POWER_MODE.value,
            parameters={"Enabled": enabled},
        )

    @staticmethod
    def set_brightness(level: float) -> ShortcutAction:
        """Set brightness for ActionBuilder."""
        return ShortcutAction(
            identifier=ActionID.SET_BRIGHTNESS.value,
            parameters={"WFBrightness": level},
        )

    @staticmethod
    def copy_to_clipboard() -> ShortcutAction:
        """Execute copy to clipboard operation for ActionBuilder."""
        return ShortcutAction(identifier=ActionID.COPY_TO_CLIPBOARD.value)

    @staticmethod
    def get_clipboard() -> ShortcutAction:
        """Retrieve clipboard from ActionBuilder."""
        return ShortcutAction(identifier=ActionID.GET_CLIPBOARD.value)

    @staticmethod
    def share() -> ShortcutAction:
        """Execute share operation for ActionBuilder."""
        return ShortcutAction(identifier=ActionID.SHARE.value)

    @staticmethod
    def notification(title: str, body: str = "") -> ShortcutAction:
        """Execute notification operation for ActionBuilder."""
        params: Dict[str, Any] = {"WFNotificationActionTitle": title}
        if body:
            params["WFNotificationActionBody"] = body
        return ShortcutAction(identifier=ActionID.SHOW_NOTIFICATION.value, parameters=params)

    @staticmethod
    def replace_text(find: str, replace: str,
                     is_regex: bool = False) -> ShortcutAction:
        """Execute replace text operation for ActionBuilder."""
        return ShortcutAction(
            identifier=ActionID.REPLACE_TEXT.value,
            parameters={
                "WFReplaceTextFind": find,
                "WFReplaceTextReplace": replace,
                "WFReplaceTextRegularExpression": is_regex,
            },
        )

    @staticmethod
    def change_case(case_type: str = "UPPERCASE") -> ShortcutAction:
        """Execute change case operation for ActionBuilder."""
        return ShortcutAction(
            identifier=ActionID.CHANGE_CASE.value,
            parameters={"WFCaseType": case_type},
        )

    @staticmethod
    def run_shortcut(name: str) -> ShortcutAction:
        """Run shortcut."""
        return ShortcutAction(
            identifier=ActionID.RUN_SHORTCUT.value,
            parameters={"WFWorkflowName": name},
        )

    @staticmethod
    def if_action(condition: str = "Equals",
                  value: Any = None) -> Tuple[ShortcutAction, ShortcutAction, ShortcutAction]:
        """Create If/Otherwise/EndIf actions. Returns (if, otherwise, endif)."""
        gid = str(uuid.uuid4())
        if_act = ShortcutAction(
            identifier=ActionID.IF.value,
            parameters={"WFCondition": condition},
            group_id=gid, group_mode="start",
        )
        if value is not None:
            if_act.parameters["WFConditionalActionString"] = str(value)
        else_act = ShortcutAction(
            identifier=ActionID.IF.value,
            group_id=gid, group_mode="middle",
        )
        end_act = ShortcutAction(
            identifier=ActionID.IF.value,
            group_id=gid, group_mode="end",
        )
        return if_act, else_act, end_act

    @staticmethod
    def repeat(count: int) -> Tuple[ShortcutAction, ShortcutAction]:
        """Create Repeat/EndRepeat actions."""
        gid = str(uuid.uuid4())
        start = ShortcutAction(
            identifier=ActionID.REPEAT.value,
            parameters={"WFRepeatCount": count},
            group_id=gid, group_mode="start",
        )
        end = ShortcutAction(
            identifier=ActionID.REPEAT.value,
            group_id=gid, group_mode="end",
        )
        return start, end


def _text_token(text: str) -> Dict[str, Any]:
    """Create a WFTextTokenString from a plain string."""
    return {
        "Value": {"attachmentsByRange": {}, "string": text},
        "WFSerializationType": "WFTextTokenString",
    }


# ============================================================================
# 3. Shortcut Builder (DSL)
# ============================================================================

@dataclass
class ShortcutDefinition:
    """A complete shortcut definition."""
    name: str = "Untitled"
    icon_color: int = 4282601983  # Blue
    icon_glyph: int = 59771  # Magic wand
    actions: List[ShortcutAction] = field(default_factory=list)
    input_types: List[str] = field(default_factory=lambda: ["WFStringContentItem"])
    created_at: float = field(default_factory=time.time)

    def add(self, action: ShortcutAction) -> "ShortcutDefinition":
        """Execute add operation for ShortcutDefinition."""
        self.actions.append(action)
        return self

    def build(self) -> bytes:
        """Build the shortcut as a .shortcut plist file (binary plist)."""
        plist_data = {
            "WFWorkflowActions": [a.to_plist_dict() for a in self.actions],
            "WFWorkflowClientVersion": "2302.0.4",
            "WFWorkflowClientRelease": "2302.0.4",
            "WFWorkflowHasOutputFallback": False,
            "WFWorkflowHasShortcutInputVariables": True,
            "WFWorkflowIcon": {
                "WFWorkflowIconStartColor": self.icon_color,
                "WFWorkflowIconGlyphNumber": self.icon_glyph,
            },
            "WFWorkflowImportQuestions": [],
            "WFWorkflowInputContentItemClasses": self.input_types,
            "WFWorkflowMinimumClientVersion": 900,
            "WFWorkflowMinimumClientVersionString": "900",
            "WFWorkflowOutputContentItemClasses": [],
            "WFWorkflowTypes": [],
        }
        return plistlib.dumps(plist_data, fmt=plistlib.FMT_BINARY)

    def build_json(self) -> str:
        """Build the shortcut as JSON (for debugging)."""
        return json.dumps(
            [a.to_plist_dict() for a in self.actions],
            indent=2, default=str,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict representation."""
        return {
            "name": self.name,
            "n_actions": len(self.actions),
            "actions": [
                {"id": a.identifier, "params": list(a.parameters.keys())}
                for a in self.actions
            ],
        }


# ============================================================================
# 4. Shortcut Templates
# ============================================================================

class ShortcutTemplates:
    """Pre-built shortcut templates."""

    @staticmethod
    def battery_warning(threshold: int = 20) -> ShortcutDefinition:
        """Warn when battery is below threshold."""
        sc = ShortcutDefinition(name="Battery Warning")
        sc.add(ActionBuilder.comment("Generated by OMNI Shortcuts Builder"))
        sc.add(ActionBuilder.battery_level())
        sc.add(ActionBuilder.set_variable("batteryLevel"))
        if_act, else_act, end_act = ActionBuilder.if_action("Is Less Than", threshold)
        sc.add(if_act)
        sc.add(ActionBuilder.set_low_power_mode(True))
        sc.add(ActionBuilder.show_result(f"Battery low! Consider charging."))
        sc.add(else_act)
        sc.add(ActionBuilder.show_result(f"Battery level is fine."))
        sc.add(end_act)
        return sc

    @staticmethod
    def url_shortener(service_url: str = "https://small.cat/entries") -> ShortcutDefinition:
        """Shorten URLs using a service."""
        sc = ShortcutDefinition(name="URL Shortener")
        sc.add(ActionBuilder.comment("Generated by OMNI Shortcuts Builder"))
        sc.add(ActionBuilder.ask_for_input("Enter URL to shorten:", "URL"))
        sc.add(ActionBuilder.set_variable("inputURL"))
        sc.add(ActionBuilder.get_url(service_url, method="POST",
                                     body={"url": "{{inputURL}}"}))
        sc.add(ActionBuilder.copy_to_clipboard())
        sc.add(ActionBuilder.show_result("Shortened URL copied to clipboard!"))
        return sc

    @staticmethod
    def morning_routine() -> ShortcutDefinition:
        """Morning routine shortcut."""
        sc = ShortcutDefinition(name="Morning Routine")
        sc.add(ActionBuilder.comment("Good morning routine"))
        sc.add(ActionBuilder.set_brightness(0.7))
        sc.add(ActionBuilder.notification("Good Morning!", "Time to start the day"))
        sc.add(ActionBuilder.get_url("https://api.openweathermap.org/data/2.5/weather?q=Jakarta"))
        sc.add(ActionBuilder.show_result("Weather loaded. Have a great day!"))
        return sc

    @staticmethod
    def clap_along() -> ShortcutDefinition:
        """Clap along text transformer."""
        sc = ShortcutDefinition(name="Clap Along")
        sc.add(ActionBuilder.comment("WHAT 👏 DO 👏 YOU 👏 WANT 👏 TO 👏 SAY"))
        sc.add(ActionBuilder.ask_for_input("WHAT DO YOU WANT TO SAY?"))
        sc.add(ActionBuilder.change_case("UPPERCASE"))
        sc.add(ActionBuilder.replace_text(r"[\s]", " 👏 ", is_regex=True))
        sc.add(ActionBuilder.copy_to_clipboard())
        sc.add(ActionBuilder.show_result("Copied! 👏"))
        return sc


# ============================================================================
# 5. Main Engine
# ============================================================================

class OmniShortcutsBuilderEngine:
    """
    OMNI Shortcuts Builder Engine.

    Programmatic iOS/Apple Shortcuts creator with SwiftUI-inspired DSL.
    Build, customize, and export .shortcut files from Python.
    """

    def __init__(self, data_dir: str = ""):
        """Initialize OmniShortcutsBuilderEngine."""
        if not data_dir:
            home = os.path.expanduser("~")
            data_dir = os.path.join(home, ".omni", "shortcuts")
        os.makedirs(data_dir, exist_ok=True)

        self.data_dir = data_dir
        self.builder = ActionBuilder()
        self.templates = ShortcutTemplates()

        # State
        self._shortcuts: Dict[str, ShortcutDefinition] = {}
        self._exports: List[Dict[str, Any]] = []
        self._started_at = time.time()

    def create_shortcut(self, name: str, icon_color: int = 4282601983,
                        icon_glyph: int = 59771) -> Dict[str, Any]:
        """Create a new empty shortcut."""
        sc = ShortcutDefinition(name=name, icon_color=icon_color, icon_glyph=icon_glyph)
        self._shortcuts[name] = sc
        return {"name": name, "status": "created"}

    def add_action(self, shortcut_name: str, action_type: str,
                   params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Add an action to a shortcut."""
        sc = self._shortcuts.get(shortcut_name)
        if not sc:
            return {"error": f"Shortcut '{shortcut_name}' not found"}

        params = params or {}
        action_map = {
            "comment": lambda: self.builder.comment(params.get("text", "")),
            "show_result": lambda: self.builder.show_result(params.get("text", "")),
            "show_alert": lambda: self.builder.show_alert(
                params.get("title", ""), params.get("message", "")),
            "ask_for_input": lambda: self.builder.ask_for_input(
                params.get("prompt", ""), params.get("type", "Text")),
            "text": lambda: self.builder.text(params.get("content", "")),
            "number": lambda: self.builder.number(params.get("value", 0)),
            "get_url": lambda: self.builder.get_url(
                params.get("url", ""), params.get("method", "GET")),
            "open_url": lambda: self.builder.open_url(params.get("url", "")),
            "set_variable": lambda: self.builder.set_variable(params.get("name", "")),
            "get_variable": lambda: self.builder.get_variable(params.get("name", "")),
            "wait": lambda: self.builder.wait(params.get("seconds", 1)),
            "battery_level": lambda: self.builder.battery_level(),
            "set_low_power_mode": lambda: self.builder.set_low_power_mode(
                params.get("enabled", True)),
            "set_brightness": lambda: self.builder.set_brightness(params.get("level", 0.5)),
            "copy_to_clipboard": lambda: self.builder.copy_to_clipboard(),
            "get_clipboard": lambda: self.builder.get_clipboard(),
            "share": lambda: self.builder.share(),
            "notification": lambda: self.builder.notification(
                params.get("title", ""), params.get("body", "")),
            "replace_text": lambda: self.builder.replace_text(
                params.get("find", ""), params.get("replace", ""),
                params.get("is_regex", False)),
            "change_case": lambda: self.builder.change_case(params.get("case", "UPPERCASE")),
            "run_shortcut": lambda: self.builder.run_shortcut(params.get("name", "")),
        }

        factory = action_map.get(action_type)
        if not factory:
            return {"error": f"Unknown action type: {action_type}"}

        action = factory()
        sc.add(action)
        return {"shortcut": shortcut_name, "action": action_type, "total_actions": len(sc.actions)}

    def use_template(self, template_name: str) -> Dict[str, Any]:
        """Load a pre-built template shortcut."""
        template_map = {
            "battery_warning": self.templates.battery_warning,
            "url_shortener": self.templates.url_shortener,
            "morning_routine": self.templates.morning_routine,
            "clap_along": self.templates.clap_along,
        }

        factory = template_map.get(template_name)
        if not factory:
            return {"error": f"Unknown template: {template_name}",
                    "available": list(template_map.keys())}

        sc = factory()
        self._shortcuts[sc.name] = sc
        return sc.to_dict()

    def build(self, shortcut_name: str) -> bytes:
        """Build shortcut as binary plist (.shortcut file)."""
        sc = self._shortcuts.get(shortcut_name)
        if not sc:
            return b""
        return sc.build()

    def export(self, shortcut_name: str, path: str = "") -> str:
        """Export shortcut to .shortcut file."""
        sc = self._shortcuts.get(shortcut_name)
        if not sc:
            return ""

        if not path:
            path = os.path.join(self.data_dir, f"{shortcut_name}.shortcut")
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)

        data = sc.build()
        with open(path, "wb") as f:
            f.write(data)

        self._exports.append({
            "name": shortcut_name, "path": path,
            "size_bytes": len(data), "n_actions": len(sc.actions),
        })
        return path

    def export_json(self, shortcut_name: str) -> str:
        """Export shortcut actions as JSON for debugging."""
        sc = self._shortcuts.get(shortcut_name)
        if not sc:
            return "{}"
        return sc.build_json()

    def list_shortcuts(self) -> List[Dict[str, Any]]:
        """Performs list shortcuts operation for OmniShortcutsBuilderEngine."""
        return [sc.to_dict() for sc in self._shortcuts.values()]

    def list_templates(self) -> List[str]:
        """Performs list templates operation for OmniShortcutsBuilderEngine."""
        return ["battery_warning", "url_shortener", "morning_routine", "clap_along"]

    def list_actions(self) -> List[str]:
        """Performs list actions operation for OmniShortcutsBuilderEngine."""
        return [a.value for a in ActionID]

    def diagnostics(self) -> Dict[str, Any]:
        """Performs diagnostics operation for OmniShortcutsBuilderEngine."""
        return {
            "engine": "OmniShortcutsBuilderEngine",
            "version": ENGINE_VERSION,
            "status": "operational",
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self._started_at)),
            "stats": {
                "created_shortcuts": len(self._shortcuts),
                "total_exports": len(self._exports),
                "total_actions_defined": sum(len(sc.actions) for sc in self._shortcuts.values()),
            },
            "available_templates": self.list_templates(),
            "available_actions": len(ActionID),
            "capabilities": [
                "shortcut_creation", "binary_plist_export", "json_export",
                "template_library", "conditional_logic", "repeat_loops",
                "variable_management", "http_requests", "text_manipulation",
                "device_control", "clipboard_operations", "notifications",
                "share_sheet", "custom_icons", "swiftui_inspired_dsl",
                "battery_monitoring", "url_encoding", "file_operations",
            ],
        }
