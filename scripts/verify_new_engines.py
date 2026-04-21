#!/usr/bin/env python3
"""Verify all 11 newly created engines from Batches 28-31."""
import importlib.util
import os
import sys

BASE = r"c:\Users\IKYY\Downloads\Omni\src\compute\python_core"

ENGINES = [
    ("omni_nymphcast_engine", "OmniNymphcastEngine"),
    ("omni_matchering_engine", "OmniMatcheringEngine"),
    ("omni_bento4_engine", "OmniBento4Engine"),
    ("omni_fluent_flyout_engine", "OmniFluentFlyoutEngine"),
    ("omni_mkchromecast_engine", "OmniMkchromecastEngine"),
    ("omni_riffusion_engine", "OmniRiffusionEngine"),
    ("omni_audiomentations_engine", "OmniAudiomentationsEngine"),
    ("omni_freyr_downloader_engine", "OmniFreyrDownloaderEngine"),
    ("omni_audiowaveform_engine", "OmniAudiowaveformEngine"),
    ("omni_sonobus_engine", "OmniSonobusEngine"),
    ("omni_ffmpegcore_engine", "OmniFfmpegcoreEngine"),
]

ok = 0
fail = 0
for mod_name, cls_name in ENGINES:
    fp = os.path.join(BASE, mod_name + ".py")
    try:
        spec = importlib.util.spec_from_file_location(mod_name, fp)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        cls = getattr(mod, cls_name)
        inst = cls()
        if hasattr(inst, "evaluate_health"):
            h = inst.evaluate_health()
        else:
            h = inst.diagnostics()
        status = h.get("status", "unknown")
        print(f"  OK  {cls_name}: {status}")
        ok += 1
    except Exception as e:
        print(f"  FAIL {cls_name}: {e}")
        fail += 1

print(f"\nResult: {ok} passed, {fail} failed out of {len(ENGINES)}")
