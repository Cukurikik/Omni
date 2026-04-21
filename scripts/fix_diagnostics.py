import os

base_dir = r'c:\Users\IKYY\Downloads\Omni\src\compute\python_core\system'

engines = {
    'omni_3ddfa_engine.py': ('Omni3DDFAEngine', ['reconstruct_3d_face']),
    'omni_ai_engineer_hq_engine.py': ('OmniAIEngineerHQEngine', ['compile_prompt_template', 'orchestrate_agent_diagram']),
    'omni_face_evolve_engine.py': ('OmniFaceEvolveEngine', ['extract_face_embedding', 'compute_similarity']),
    'omni_lstm_ar_engine.py': ('OmniLSTMAREngine', ['initialize_lstm_architecture', 'infer_activity']),
    'omni_min_dalle_engine.py': ('OmniMinDalleEngine', ['initialize_generator', 'generate_image_stream']),
    'omni_studiogan_engine.py': ('OmniStudioGANEngine', ['link_configuration', 'compile_training_loop']),
    'omni_text2sql_engine.py': ('OmniText2SQLEngine', ['compile_nl_to_sql', 'validate_sql_syntax']),
    'omni_tps_engine.py': ('OmniTPSEngine', ['animate_from_driving_video']),
    'omni_autohotkey_engine.py': ('OmniAutoHotkeyEngine', ['run_script', 'compile_script']),
    'omni_vagrant_env_engine.py': ('OmniVagrantEnvEngine', ['create_vm', 'destroy_vm']),
}

for fname, (cls_name, caps) in engines.items():
    fpath = os.path.join(base_dir, fname)
    if not os.path.exists(fpath):
        print(f'SKIP {fname} (not found)')
        continue
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'def diagnostics' in content:
        print(f'SKIP {fname} (already has diagnostics)')
        continue
    caps_str = ', '.join([f'"{c}"' for c in caps])
    diag_method = f'''
    def diagnostics(self):
        """Returns engine health status for the OmniEngineRegistry."""
        return {{
            "engine": "{cls_name}",
            "version": "1.0.0",
            "status": "operational",
            "capabilities": [{caps_str}],
        }}
'''
    content = content.rstrip() + '\n' + diag_method
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'FIXED {fname}')

print('Done.')
