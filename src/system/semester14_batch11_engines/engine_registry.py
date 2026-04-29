class OmniResult:
    def __init__(self, value, error=None):
        self.value = value
        self.error = error
        self.is_ok = error is None

BATCH11_ENGINES = {
    "GraphGPT": "system.graphgpt.graph_tensor_ops",
    "LongMem": "compute.longmem.longmem_attention",
    "FineTuningLLMs": "system.finetuningllms.lora_adapter",
    "AwesomeQuant": "system.quantpapers.w4a8_quantizer",
    "TreeOfThought": "compute.totprompt.tot_search",
    "LLMRobust": "system.llmrobust.uncertainty_metric",
    "makeMoE": "system.makemoe.sparse_router",
    "VoxPoser": "compute.voxposer.value_map_generator",
    "SelfRefine": "compute.selfrefine.feedback_loop",
    "LLMInternals": "system.llminternals.flash_attention",
    "LightMem": "system.lightmem.lightweight_cache",
    "4KAgent": "compute.4kagent.super_res_model",
    "ParrotNvim": "system.parrotnvim.nvim_rpc",
    "JuneVoice": "compute.junevoice.whisper_tts",
    "ISCBench": "compute.iscbench.safety_evaluator",
    "Observal": "concurrency.observal.telemetry_stream",
    "MedGraphRAG": "compute.medgraphrag.evidence_retriever",
    "AgentGym": "compute.agentgym.env_simulator",
    "MiniCoding": "compute.minicoding.code_generator"
}

def register_all_engines() -> OmniResult:
    try:
        registered = []
        for engine, path in BATCH11_ENGINES.items():
            registered.append((engine, path))
        return OmniResult(registered)
    except Exception as e:
        return OmniResult(None, str(e))
