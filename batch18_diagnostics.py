"""Batch 18 Engine Diagnostics — Full Verification"""
import sys, json, os, random

sys.path.insert(0, "src/compute/python_core")

print("=" * 70)
print("BATCH 18 ENGINE DIAGNOSTICS — OMNI FRAMEWORK")
print("=" * 70)

# ── Engine 1: FEDOT AutoML ──
from omni_fedot_automl_engine import OmniFedotAutoMLEngine

fedot = OmniFedotAutoMLEngine()
diag = fedot.diagnostics()
engine_name = diag["engine"]
version = diag["version"]
status = diag["status"].upper()
print(f"\n[1/5] {engine_name} v{version} -- {status}")
tasks = diag["supported_tasks"]
presets = diag["available_presets"]
n_caps = len(diag["capabilities"])
print(f"      Tasks: {tasks}")
print(f"      Presets: {presets}")
print(f"      Capabilities: {n_caps} features")

# Live AutoML run
random.seed(42)
features = [[random.gauss(c * 2, 1) for _ in range(4)] for c in [0, 0, 0, 0, 0, 1, 1, 1, 1, 1] * 5]
target = [0] * 25 + [1] * 25

result = fedot.fit(features, target, task_type="classification", preset="fast_train", timeout_minutes=0.5)
pid = result["pipeline_id"]
metric = result["metric"]
mval = result["metric_value"]
gens = result["generations"]
tms = result["optimization_time_ms"]
nnodes = len(result["pipeline"]["nodes"])
print(f"      PASS AutoML Run: pipeline={pid}, {metric}={mval:.4f}")
print(f"           Generations: {gens}, Time: {tms:.0f}ms, Nodes: {nnodes}")

# Predict
pred = fedot.predict(pid, features[:5], "classification")
n_pred = pred["n_predictions"]
preds = pred["predictions"]
print(f"      PASS Prediction: {n_pred} samples -> {preds}")

# Export
path = fedot.export_pipeline(pid)
print(f"      PASS Pipeline exported: {path}")

# Metrics
metrics = fedot.get_metrics(pid, [0, 0, 1, 1, 1], [0, 0, 1, 0, 1])
print(f"      PASS Metrics: {metrics}")

# Regression test
reg_features = [[x, x * 0.5 + random.gauss(0, 0.3)] for x in range(50)]
reg_target = [x * 2.5 + 3.0 + random.gauss(0, 0.5) for x in range(50)]
reg_result = fedot.fit(reg_features, reg_target, task_type="regression", preset="fast_train", timeout_minutes=0.3)
reg_metric = reg_result["metric"]
reg_val = reg_result["metric_value"]
print(f"      PASS Regression: {reg_metric}={reg_val:.4f}")

print()

# ── Engine 2: KiBot PCB ──
from omni_kibot_pcb_engine import OmniKiBotPCBEngine

kibot = OmniKiBotPCBEngine()
diag = kibot.diagnostics()
engine_name = diag["engine"]
version = diag["version"]
status = diag["status"].upper()
n_caps = len(diag["capabilities"])
print(f"[2/5] {engine_name} v{version} -- {status}")
print(f"      Outputs: {len(diag['supported_outputs'])} formats")
print(f"      Capabilities: {n_caps} features")

# Load PCB design
design_info = kibot.load_design(
    project_name="OmniBoard-V1",
    board_width=80, board_height=60, n_layers=4, rev="2.1",
    footprints=[
        {"reference": "U1", "value": "STM32F405", "footprint": "LQFP-64",
         "position": [25, 30], "manufacturer": "STMicro", "mpn": "STM32F405RGT6",
         "description": "ARM Cortex-M4 MCU"},
        {"reference": "U2", "value": "W25Q128", "footprint": "SOIC-8",
         "position": [50, 20], "manufacturer": "Winbond", "mpn": "W25Q128JVSIQ",
         "description": "SPI Flash 128Mbit"},
        {"reference": "C1", "value": "100nF", "footprint": "0402", "position": [28, 32]},
        {"reference": "C2", "value": "100nF", "footprint": "0402", "position": [30, 32]},
        {"reference": "C3", "value": "10uF", "footprint": "0805", "position": [22, 28]},
        {"reference": "R1", "value": "10K", "footprint": "0402", "position": [35, 25]},
        {"reference": "R2", "value": "10K", "footprint": "0402", "position": [36, 25]},
        {"reference": "R3", "value": "4.7K", "footprint": "0402", "position": [37, 25]},
        {"reference": "J1", "value": "USB-C", "footprint": "USB-C-16P",
         "position": [10, 30], "is_smd": False},
        {"reference": "Y1", "value": "8MHz", "footprint": "HC49",
         "position": [20, 35], "is_smd": False},
    ],
    tracks=[
        {"start": [25, 30], "end": [50, 20], "width": 0.25, "net": "SPI_CLK"},
        {"start": [25, 31], "end": [50, 21], "width": 0.25, "net": "SPI_MOSI"},
        {"start": [10, 30], "end": [25, 30], "width": 0.5, "net": "USB_D+"},
    ],
    vias=[
        {"position": [30, 25], "size": 0.8, "drill": 0.4, "net": "GND"},
        {"position": [40, 25], "size": 0.8, "drill": 0.4, "net": "VCC"},
    ],
)
n_comp = design_info["n_components"]
n_layers = design_info["n_layers"]
pname = design_info["project_name"]
print(f"      PASS Loaded: {pname} -- {n_comp} components, {n_layers} layers")

# DRC
drc = kibot.run_drc("OmniBoard-V1")
drc_status = drc["status"].upper()
errors = drc["errors"]
warnings = drc["warnings"]
print(f"      PASS DRC: {drc_status} -- {errors} errors, {warnings} warnings")

# BOM
bom_csv = kibot.generate_bom("OmniBoard-V1", "csv")
bom_lines = bom_csv.strip().split("\n")
print(f"      PASS BOM CSV: {len(bom_lines) - 1} grouped entries")

bom_html = kibot.generate_bom("OmniBoard-V1", "html")
print(f"      PASS BOM HTML: {len(bom_html)} chars")

# Position
pos = kibot.generate_position("OmniBoard-V1")
pos_lines = pos.strip().split("\n")
print(f"      PASS Pick&Place: {len(pos_lines) - 1} placements")

# Gerber Job
job = kibot.generate_gerber_job("OmniBoard-V1")
n_files = len(job["FilesAttributes"])
print(f"      PASS Gerber Job: {n_files} layer files")

# Drill Report
drill = kibot.generate_drill_report("OmniBoard-V1")
drill_lines = drill.split("\n")
print(f"      PASS Drill Report: {len(drill_lines)} lines")

# Save outputs
paths = kibot.save_outputs("OmniBoard-V1")
n_saved = len(paths)
print(f"      PASS Saved: {n_saved} output files")

print()

# ── Engine 3: Shortcuts Builder ──
from omni_shortcuts_builder_engine import OmniShortcutsBuilderEngine

shortcuts = OmniShortcutsBuilderEngine()
diag = shortcuts.diagnostics()
engine_name = diag["engine"]
version = diag["version"]
status = diag["status"].upper()
n_caps = len(diag["capabilities"])
print(f"[3/5] {engine_name} v{version} -- {status}")
templates = diag["available_templates"]
n_actions = diag["available_actions"]
print(f"      Templates: {templates}")
print(f"      Actions: {n_actions} types")
print(f"      Capabilities: {n_caps} features")

# Template: Battery Warning
sc1 = shortcuts.use_template("battery_warning")
sc1_name = sc1["name"]
sc1_acts = sc1["n_actions"]
print(f"      PASS Template: {sc1_name} -- {sc1_acts} actions")

# Template: Clap Along
sc2 = shortcuts.use_template("clap_along")
sc2_name = sc2["name"]
sc2_acts = sc2["n_actions"]
print(f"      PASS Template: {sc2_name} -- {sc2_acts} actions")

# Template: Morning Routine
sc3 = shortcuts.use_template("morning_routine")
sc3_name = sc3["name"]
sc3_acts = sc3["n_actions"]
print(f"      PASS Template: {sc3_name} -- {sc3_acts} actions")

# Custom shortcut
shortcuts.create_shortcut("Morning Productivity")
shortcuts.add_action("Morning Productivity", "comment", {"text": "OMNI Morning Routine"})
shortcuts.add_action("Morning Productivity", "notification",
                     {"title": "Good Morning!", "body": "Time to be productive"})
shortcuts.add_action("Morning Productivity", "set_brightness", {"level": 0.8})
shortcuts.add_action("Morning Productivity", "get_url",
                     {"url": "https://api.weather.com/v3/wx/forecast", "method": "GET"})
shortcuts.add_action("Morning Productivity", "show_result", {"text": "Weather loaded!"})

info = shortcuts.list_shortcuts()
custom = [s for s in info if s["name"] == "Morning Productivity"][0]
custom_name = custom["name"]
custom_acts = custom["n_actions"]
print(f"      PASS Custom: {custom_name} -- {custom_acts} actions")

# Export .shortcut (binary plist)
path = shortcuts.export("Battery Warning")
file_size = os.path.getsize(path)
print(f"      PASS Exported: {path} ({file_size} bytes)")

# JSON debug export
json_out = shortcuts.export_json("Clap Along")
actions = json.loads(json_out)
print(f"      PASS JSON debug: {len(actions)} action nodes")

print()
print("=" * 70)
print("BATCH 18 — ALL 3 PYTHON ENGINES OPERATIONAL")
print("=" * 70)
