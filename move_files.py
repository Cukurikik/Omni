import os
import shutil

base_dir = r"C:\Users\IKYY\Downloads\Omni\src"

moves = [
    (r"compute\semester_13\batch_05\meme_clip_feature_extractor.py", r"compute\memeclip", "mod.py"),
    (r"compute\semester_13\batch_05\described_visual_interpreter.py", r"compute\described", "mod.py"),
    (r"compute\semester_13\batch_05\meld_feature_fusion.py", r"compute\meld", "mod.py"),
    (r"compute\semester_13\batch_05\qwen_lens_reasoning_core.py", r"compute\qwen_lens", "mod.py"),
    (r"compute\semester_13\batch_05\aestetik_spatial_encoder.py", r"compute\aestetik", "mod.py"),
    (r"compute\semester_13\batch_05\slp_waveform_processor.py", r"compute\slp", "mod.py"),
    (r"compute\semester_13\batch_05\trim_compression_ratio.py", r"compute\trim", "mod.py"),
    (r"compute\semester_13\batch_05\mb2c_robustness_metric.py", r"compute\mb2c", "mod.py"),
    (r"compute\semester_13\batch_05\dsec_mos_event_filter.py", r"compute\dsec_mos", "mod.py"),
    (r"compute\semester_13\batch_05\msiflow_spectrum_analyzer.py", r"compute\msiflow", "mod.py"),

    (r"system\semester_13\batch_05\paper_notes_memory_allocator.cpp", r"system\papernotes", "mod.cpp"),
    (r"system\semester_13\batch_05\multimodal_dialog_tracker.rs", r"system\multimodal_dialog", "mod.rs"),
    (r"system\semester_13\batch_05\multibanana_gpu_manager.cpp", r"system\multibanana", "mod.cpp"),
    (r"system\semester_13\batch_05\chart_museum_renderer.rs", r"system\chart_museum", "mod.rs"),
    (r"system\semester_13\batch_05\superpilot_memory_sandbox.cpp", r"system\superpilot", "mod.cpp"),

    (r"concurrency\semester_13\batch_05\eipy_ensemble_scheduler.go", r"concurrency\eipy", "mod.go"),
    (r"concurrency\semester_13\batch_05\sigir_product_streamer.go", r"concurrency\sigir_streamer", "mod.go"),
    (r"concurrency\semester_13\batch_05\gen_ai_pipeline_broker.go", r"concurrency\gen_ai_pipeline", "mod.go"),
    (r"concurrency\semester_13\batch_05\text2img_parallel_generator.go", r"concurrency\text2img", "mod.go"),
    (r"concurrency\semester_13\batch_05\multi_agent_vqa_dispatcher.go", r"concurrency\multi_agent_vqa", "mod.go"),

    (r"domain\semester_13\batch_05\MemeClipDomainPolicy.cs", r"domain\memeclip", "mod.cs"),
    (r"domain\semester_13\batch_05\DescribedCaptionRule.cs", r"domain\described", "mod.cs"),
    (r"domain\semester_13\batch_05\MeldEthicsValidator.cs", r"domain\meld", "mod.cs"),
    (r"domain\semester_13\batch_05\QwenLensContextPolicy.cs", r"domain\qwen_lens", "mod.cs"),
    (r"domain\semester_13\batch_05\AestetikBioMarkerRules.cs", r"domain\aestetik", "mod.cs"),

    (r"ui\semester_13\batch_05\slp_audio_visualizer.ts", r"ui\slp", "mod.ts"),
    (r"ui\semester_13\batch_05\trim_compression_dashboard.ts", r"ui\trim", "mod.ts"),
    (r"ui\semester_13\batch_05\mb2c_network_graph.ts", r"ui\mb2c", "mod.ts"),
    (r"ui\semester_13\batch_05\dsec_mos_event_cam_viewer.ts", r"ui\dsec_mos", "mod.ts"),
    (r"ui\semester_13\batch_05\msiflow_spectrum_canvas.ts", r"ui\msiflow", "mod.ts")
]

for src_rel, dest_folder_rel, filename in moves:
    src = os.path.join(base_dir, src_rel)
    dest_dir = os.path.join(base_dir, dest_folder_rel)
    dest_file = os.path.join(dest_dir, filename)

    if os.path.exists(src):
        os.makedirs(dest_dir, exist_ok=True)
        shutil.move(src, dest_file)
        print(f"Moved {src} -> {dest_file}")
    else:
        print(f"Source missing: {src}")

for layer in ["compute", "system", "concurrency", "domain", "ui"]:
    sem_dir = os.path.join(base_dir, layer, "semester_13")
    if os.path.exists(sem_dir):
        shutil.rmtree(sem_dir)
        print(f"Removed clean {sem_dir}")
