// ===========================================================================
// OMNI AI PROJECT NAVIGATOR ENGINE (SEMESTER 5 — BATCH 11)
// ===========================================================================
// Absorbed From  : ashishpatel26/500-AI-Machine-learning-Deep-learning-Computer-vision-NLP-Projects-with-code
// Logic Inherited: Interface Layer (AI Domain Router & Project Discovery)
// ===========================================================================
//
// KNOWLEDGE ABSORBED:
//   The 500-AI repository is a curated encyclopedia of real-world AI/ML/DL
//   projects spanning Vision, NLP, Audio, Tabular, Reinforcement Learning,
//   and Generative AI. OMNI absorbs its classification taxonomy to build
//   a meta-router: given a problem description, route to the correct OMNI
//   Compute Layer engine automatically.
//

export type AIDomain =
    | "computer_vision"
    | "nlp"
    | "audio"
    | "tabular"
    | "reinforcement_learning"
    | "generative";

export interface ProjectEntry {
    id: string;
    title: string;
    domain: AIDomain;
    keywords: string[];
    targetEngine: string;
    complexity: "beginner" | "intermediate" | "advanced";
}

export interface RoutingResult {
    domain: AIDomain;
    targetEngine: string;
    confidence: number;
    matchedKeywords: string[];
}

// Domain keyword registry derived from 500+ AI project titles
const DOMAIN_KEYWORDS: Record<AIDomain, string[]> = {
    computer_vision: [
        "image", "object", "detection", "segmentation", "face", "pose",
        "yolo", "cnn", "resnet", "vgg", "opencv", "bounding", "box",
        "classification", "recognition", "tracking", "ocr", "openpose",
        "diffusion", "gan", "style", "transfer", "super", "resolution"
    ],
    nlp: [
        "text", "sentiment", "ner", "named", "entity", "tokenize",
        "language", "translation", "summarization", "question", "answer",
        "bert", "gpt", "transformer", "spacy", "nlp", "chatbot",
        "embedding", "word2vec", "corpus", "document", "speech"
    ],
    audio: [
        "audio", "sound", "music", "voice", "tts", "asr", "speech",
        "waveform", "spectrogram", "midi", "cloning", "synthesis",
        "mel", "vocoder", "frequency", "noise", "cancellation"
    ],
    tabular: [
        "tabular", "csv", "regression", "prediction", "forecast",
        "xgboost", "random", "forest", "linear", "logistic",
        "feature", "engineering", "time", "series", "stock", "price",
        "recommendation", "collaborative", "filtering"
    ],
    reinforcement_learning: [
        "reinforcement", "rl", "agent", "reward", "policy",
        "q-learning", "dqn", "ppo", "environment", "gym",
        "atari", "game", "robot", "navigation", "simulation"
    ],
    generative: [
        "generative", "gan", "vae", "diffusion", "stable",
        "midjourney", "dalle", "image", "generation", "creative",
        "art", "deepfake", "inpainting", "outpainting"
    ],
};

// Engine routing table: domain → best OMNI Compute engine
const ENGINE_ROUTING: Record<AIDomain, string> = {
    computer_vision: "omni_vision_analytics_engine",
    nlp: "omni_spacy_nlp_engine",
    audio: "omni_vits_synthesis_engine",
    tabular: "omni_quant_finance_engine",
    reinforcement_learning: "omni_distributed_compute_engine",
    generative: "omni_diffusion_pipeline_engine",
};

// Curated project catalog (representative subset of 500-AI)
const PROJECT_CATALOG: ProjectEntry[] = [
    { id: "p001", title: "Real-time Face Detection with OpenCV", domain: "computer_vision", keywords: ["face", "detection", "opencv"], targetEngine: "omni_vision_analytics_engine", complexity: "beginner" },
    { id: "p002", title: "Sentiment Analysis with BERT", domain: "nlp", keywords: ["sentiment", "bert", "text"], targetEngine: "omni_spacy_nlp_engine", complexity: "intermediate" },
    { id: "p003", title: "Music Genre Classification", domain: "audio", keywords: ["music", "audio", "classification"], targetEngine: "omni_vits_synthesis_engine", complexity: "intermediate" },
    { id: "p004", title: "Stock Price Prediction with LSTM", domain: "tabular", keywords: ["stock", "price", "prediction", "time", "series"], targetEngine: "omni_quant_finance_engine", complexity: "advanced" },
    { id: "p005", title: "Atari Game Agent with DQN", domain: "reinforcement_learning", keywords: ["atari", "game", "dqn", "agent"], targetEngine: "omni_distributed_compute_engine", complexity: "advanced" },
    { id: "p006", title: "Stable Diffusion Image Generation", domain: "generative", keywords: ["stable", "diffusion", "generation", "image"], targetEngine: "omni_diffusion_pipeline_engine", complexity: "advanced" },
    { id: "p007", title: "Multi-Person Pose Estimation", domain: "computer_vision", keywords: ["pose", "openpose", "detection"], targetEngine: "omni_openpose_body_engine", complexity: "advanced" },
    { id: "p008", title: "Named Entity Recognition Pipeline", domain: "nlp", keywords: ["ner", "named", "entity", "spacy"], targetEngine: "omni_spacy_nlp_engine", complexity: "beginner" },
    { id: "p009", title: "Zero-Shot Image Classification", domain: "computer_vision", keywords: ["classification", "clip", "image"], targetEngine: "omni_clip_embedding_engine", complexity: "intermediate" },
    { id: "p010", title: "Voice Cloning System", domain: "audio", keywords: ["voice", "cloning", "synthesis", "tts"], targetEngine: "omni_voice_cloning_engine", complexity: "advanced" },
];


export class OmniAIProjectNavigatorEngine {
    private catalog: ProjectEntry[];

    constructor() {
        this.catalog = [...PROJECT_CATALOG];
    }

    /**
     * Routes a problem description to the best OMNI engine.
     * Uses keyword frequency matching across all AI domains.
     *
     * @param description - Natural language description of the AI problem.
     * @returns Routing result with domain, target engine, and confidence.
     */
    public routeProblem(description: string): { success: boolean; value?: RoutingResult; error?: Error } {
        if (!description || description.trim().length === 0) {
            return { success: false, error: new Error("Problem description cannot be empty.") };
        }

        const tokens = description.toLowerCase().split(/\s+/);
        const domainScores: Record<AIDomain, { score: number; matched: string[] }> = {
            computer_vision: { score: 0, matched: [] },
            nlp: { score: 0, matched: [] },
            audio: { score: 0, matched: [] },
            tabular: { score: 0, matched: [] },
            reinforcement_learning: { score: 0, matched: [] },
            generative: { score: 0, matched: [] },
        };

        for (const token of tokens) {
            for (const [domain, keywords] of Object.entries(DOMAIN_KEYWORDS)) {
                if (keywords.includes(token)) {
                    const d = domain as AIDomain;
                    domainScores[d].score += 1;
                    if (!domainScores[d].matched.includes(token)) {
                        domainScores[d].matched.push(token);
                    }
                }
            }
        }

        // Find best domain
        let bestDomain: AIDomain = "computer_vision";
        let bestScore = 0;
        for (const [domain, info] of Object.entries(domainScores)) {
            if (info.score > bestScore) {
                bestScore = info.score;
                bestDomain = domain as AIDomain;
            }
        }

        const totalTokens = tokens.length;
        const confidence = totalTokens > 0 ? Math.min(1.0, bestScore / Math.max(totalTokens * 0.3, 1)) : 0;

        return {
            success: true,
            value: {
                domain: bestDomain,
                targetEngine: ENGINE_ROUTING[bestDomain],
                confidence: Math.round(confidence * 1000) / 1000,
                matchedKeywords: domainScores[bestDomain].matched,
            },
        };
    }

    /**
     * Searches the project catalog by keyword.
     */
    public searchProjects(query: string): { success: boolean; value?: ProjectEntry[] } {
        const q = query.toLowerCase();
        const results = this.catalog.filter(
            (p) => p.title.toLowerCase().includes(q) ||
                   p.keywords.some((k) => k.includes(q))
        );
        return { success: true, value: results };
    }

    /**
     * Lists all projects in a given domain.
     */
    public listByDomain(domain: AIDomain): { success: boolean; value?: ProjectEntry[] } {
        return { success: true, value: this.catalog.filter((p) => p.domain === domain) };
    }

    /**
     * Returns catalog statistics.
     */
    public getStats(): Record<string, any> {
        const domainCounts: Record<string, number> = {};
        for (const p of this.catalog) {
            domainCounts[p.domain] = (domainCounts[p.domain] || 0) + 1;
        }
        return {
            totalProjects: this.catalog.length,
            domains: Object.keys(DOMAIN_KEYWORDS).length,
            domainDistribution: domainCounts,
        };
    }

    public evaluateHealth(): Record<string, any> {
        return {
            engine: "OmniAIProjectNavigatorEngine",
            layer: "Interface",
            status: "healthy",
            catalogSize: this.catalog.length,
            supportedDomains: Object.keys(DOMAIN_KEYWORDS).length,
            learned_from: "ashishpatel26/500-AI-Projects",
        };
    }

    // --- Registry Interface ---
    diagnostics(): Record<string, unknown> {
        return {
            engine: "OmniAIProjectNavigatorEngine",
            version: "1.0.0",
            status: "operational",
            layer: "ui",
            language: "TypeScript",
        };
    }
}
