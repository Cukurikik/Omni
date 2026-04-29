# Engine Registry for Semester 14 Batch 9
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

BATCH9_ENGINES = [
    {"id": "omni-kvpress-engine-s14b9", "repo": "NVIDIA/kvpress", "domain": "kv-cache-compression"},
    {"id": "omni-embed-anything-engine-s14b9", "repo": "StarlightSearch/EmbedAnything", "domain": "embedding-inference"},
    {"id": "omni-sophia-engine-s14b9", "repo": "Liuhong99/Sophia", "domain": "second-order-optimizer"},
    {"id": "omni-visionllm-engine-s14b9", "repo": "OpenGVLab/VisionLLM", "domain": "vision-language-detection"},
    {"id": "omni-pointllm-engine-s14b9", "repo": "InternRobotics/PointLLM", "domain": "3d-point-cloud"},
    {"id": "omni-llm-blender-engine-s14b9", "repo": "yuchenlin/LLM-Blender", "domain": "llm-ensemble"},
    {"id": "omni-langkit-engine-s14b9", "repo": "whylabs/langkit", "domain": "llm-monitoring"},
    {"id": "omni-webllm-engine-s14b9", "repo": "mlc-ai/web-llm-chat", "domain": "browser-llm"},
    {"id": "omni-hackingbuddy-engine-s14b9", "repo": "ipa-lab/hackingBuddyGPT", "domain": "llm-pentesting"},
    {"id": "omni-autollm-engine-s14b9", "repo": "viddexa/autollm", "domain": "rag-webapp"},
    {"id": "omni-qwen-math-engine-s14b9", "repo": "QwenLM/Qwen2.5-Math", "domain": "math-reasoning"},
    {"id": "omni-xrayglm-engine-s14b9", "repo": "WangRongsheng/XrayGLM", "domain": "medical-vision"},
    {"id": "omni-sharegpt4video-engine-s14b9", "repo": "ShareGPT4Omni/ShareGPT4Video", "domain": "video-understanding"},
    {"id": "omni-llm-pruner-engine-s14b9", "repo": "horseee/LLM-Pruner", "domain": "structural-pruning"},
    {"id": "omni-llm-sandbox-engine-s14b9", "repo": "vndee/llm-sandbox", "domain": "code-sandbox"},
    {"id": "omni-viscpm-engine-s14b9", "repo": "OpenBMB/VisCPM", "domain": "multilingual-vision"},
    {"id": "omni-caregpt-engine-s14b9", "repo": "WangRongsheng/CareGPT", "domain": "medical-llm"},
    {"id": "omni-lawyer-llama-engine-s14b9", "repo": "AndrewZhe/lawyer-llama", "domain": "legal-llm"},
    {"id": "omni-hallucination-engine-s14b9", "repo": "HillZhang1999/llm-hallucination-survey", "domain": "hallucination-detection"},
    {"id": "omni-llm4ie-engine-s14b9", "repo": "quqxui/Awesome-LLM4IE-Papers", "domain": "information-extraction"},
    {"id": "omni-graph-llm-engine-s14b9", "repo": "PeterGriffinJin/Awesome-Language-Model-on-Graphs", "domain": "graph-llm"},
    {"id": "omni-prompt4reason-engine-s14b9", "repo": "zjunlp/Prompt4ReasoningPapers", "domain": "reasoning-prompts"},
    {"id": "omni-llm-survey-engine-s14b9", "repo": "RUCAIBox/LLMSurvey", "domain": "llm-survey"},
    {"id": "omni-llm-agent-engine-s14b9", "repo": "Paitesanshi/LLM-Agent-Survey", "domain": "agent-survey"},
    {"id": "omni-llm-safety-engine-s14b9", "repo": "ydyjya/Awesome-LLM-Safety", "domain": "llm-safety"},
    {"id": "omni-llm-workshop-engine-s14b9", "repo": "rasbt/LLM-workshop-2024", "domain": "llm-education"},
    {"id": "omni-role-playing-engine-s14b9", "repo": "Neph0s/awesome-llm-role-playing-with-persona", "domain": "persona-roleplay"},
    {"id": "omni-foundation-models-engine-s14b9", "repo": "rudrankriyam/Foundation-Models-Framework-Example", "domain": "foundation-models"},
    {"id": "omni-llm-inference-engine-s14b9", "repo": "DefTruth/Awesome-LLM-Inference", "domain": "llm-inference"},
    {"id": "omni-tinyllm-engine-s14b9", "repo": "jzhang38/TinyLlama", "domain": "small-llm"},
]

def get_all_engines():
    return BATCH9_ENGINES

def get_engine_count():
    return len(BATCH9_ENGINES)
