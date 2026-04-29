// ===========================================================================
// OMNI AI CAREER ROADMAP ENGINE (SEMESTER 5 — BATCH 12)
// ===========================================================================
// Absorbed From  : AMAI-GmbH/AI-Expert-Roadmap
// Logic Inherited: Interface Layer (AI Skill Tree & Learning Path Router)
// ===========================================================================
//
// KNOWLEDGE ABSORBED:
//   The AI-Expert-Roadmap defines a structured learning path:
//     Fundamentals → Data Science → Machine Learning → Deep Learning
//     → Specialization (NLP, CV, RL, MLOps, etc.)
//   Each node has prerequisites, difficulty, and estimated hours.
//   OMNI absorbs this to build a dynamic skill assessment and
//   personalized learning path recommendation engine.
//

export type SkillLevel = "beginner" | "intermediate" | "advanced" | "expert";
export type SkillDomain = "fundamentals" | "data_science" | "machine_learning" | "deep_learning" | "nlp" | "computer_vision" | "mlops" | "reinforcement_learning";

export interface SkillNode {
    id: string;
    name: string;
    domain: SkillDomain;
    level: SkillLevel;
    prerequisites: string[];
    estimatedHours: number;
    description: string;
    omniEngine?: string;    // Maps to relevant OMNI engine
}

export interface LearningPath {
    userId: string;
    targetRole: string;
    requiredSkills: SkillNode[];
    completedSkills: string[];
    totalHours: number;
    progressPercent: number;
}

// Comprehensive AI skill tree (from AI-Expert-Roadmap)
const SKILL_TREE: SkillNode[] = [
    // Fundamentals
    { id: "math_linear_algebra", name: "Linear Algebra", domain: "fundamentals", level: "beginner", prerequisites: [], estimatedHours: 40, description: "Vectors, matrices, eigenvalues, SVD" },
    { id: "math_calculus", name: "Calculus & Optimization", domain: "fundamentals", level: "beginner", prerequisites: [], estimatedHours: 30, description: "Derivatives, gradients, chain rule, backpropagation math" },
    { id: "math_probability", name: "Probability & Statistics", domain: "fundamentals", level: "beginner", prerequisites: [], estimatedHours: 35, description: "Distributions, Bayes theorem, hypothesis testing" },
    { id: "prog_python", name: "Python Programming", domain: "fundamentals", level: "beginner", prerequisites: [], estimatedHours: 60, description: "Core Python, NumPy, Pandas, Matplotlib" },

    // Data Science
    { id: "ds_eda", name: "Exploratory Data Analysis", domain: "data_science", level: "intermediate", prerequisites: ["prog_python", "math_probability"], estimatedHours: 25, description: "Data cleaning, visualization, feature discovery" },
    { id: "ds_feature_eng", name: "Feature Engineering", domain: "data_science", level: "intermediate", prerequisites: ["ds_eda"], estimatedHours: 20, description: "Feature selection, transformation, encoding" },

    // Machine Learning
    { id: "ml_supervised", name: "Supervised Learning", domain: "machine_learning", level: "intermediate", prerequisites: ["math_linear_algebra", "math_calculus", "ds_eda"], estimatedHours: 50, description: "Regression, classification, SVM, decision trees, ensembles", omniEngine: "omni_mlops_pipeline_engine" },
    { id: "ml_unsupervised", name: "Unsupervised Learning", domain: "machine_learning", level: "intermediate", prerequisites: ["ml_supervised"], estimatedHours: 30, description: "K-means, PCA, DBSCAN, autoencoders" },
    { id: "ml_evaluation", name: "Model Evaluation", domain: "machine_learning", level: "intermediate", prerequisites: ["ml_supervised"], estimatedHours: 15, description: "Cross-validation, ROC/AUC, precision/recall, F1" },

    // Deep Learning
    { id: "dl_basics", name: "Neural Network Fundamentals", domain: "deep_learning", level: "intermediate", prerequisites: ["ml_supervised", "math_calculus"], estimatedHours: 40, description: "Perceptron, backprop, activation functions, loss", omniEngine: "omni_tensor_primitive_engine" },
    { id: "dl_cnn", name: "Convolutional Neural Networks", domain: "deep_learning", level: "advanced", prerequisites: ["dl_basics"], estimatedHours: 35, description: "Conv layers, pooling, ResNet, transfer learning", omniEngine: "omni_vision_analytics_engine" },
    { id: "dl_rnn", name: "Recurrent Neural Networks", domain: "deep_learning", level: "advanced", prerequisites: ["dl_basics"], estimatedHours: 30, description: "LSTM, GRU, sequence modeling" },
    { id: "dl_transformer", name: "Transformers & Attention", domain: "deep_learning", level: "advanced", prerequisites: ["dl_rnn"], estimatedHours: 45, description: "Self-attention, BERT, GPT architecture", omniEngine: "omni_llm_core_engine" },

    // Specializations
    { id: "nlp_core", name: "NLP Pipeline", domain: "nlp", level: "advanced", prerequisites: ["dl_transformer"], estimatedHours: 40, description: "Tokenization, NER, POS tagging, dependency parsing", omniEngine: "omni_spacy_nlp_engine" },
    { id: "cv_detection", name: "Object Detection", domain: "computer_vision", level: "advanced", prerequisites: ["dl_cnn"], estimatedHours: 35, description: "YOLO, SSD, Faster R-CNN", omniEngine: "omni_vision_analytics_engine" },
    { id: "cv_pose", name: "Human Pose Estimation", domain: "computer_vision", level: "expert", prerequisites: ["cv_detection"], estimatedHours: 25, description: "OpenPose, bottom-up vs top-down", omniEngine: "omni_openpose_body_engine" },
    { id: "gen_diffusion", name: "Diffusion Models", domain: "deep_learning", level: "expert", prerequisites: ["dl_transformer"], estimatedHours: 40, description: "DDPM, Stable Diffusion, latent diffusion", omniEngine: "omni_diffusion_pipeline_engine" },
    { id: "mlops_deploy", name: "MLOps & Deployment", domain: "mlops", level: "advanced", prerequisites: ["ml_evaluation"], estimatedHours: 35, description: "Model serving, monitoring, CI/CD for ML", omniEngine: "omni_mlops_pipeline_engine" },
    { id: "rl_basics", name: "Reinforcement Learning", domain: "reinforcement_learning", level: "advanced", prerequisites: ["dl_basics", "math_probability"], estimatedHours: 50, description: "Q-learning, policy gradient, PPO, A3C", omniEngine: "omni_distributed_compute_engine" },
];

// Role definitions: what skills each AI role needs
const ROLE_REQUIREMENTS: Record<string, string[]> = {
    "ML Engineer": ["prog_python", "ml_supervised", "ml_evaluation", "dl_basics", "mlops_deploy"],
    "Data Scientist": ["prog_python", "math_probability", "ds_eda", "ds_feature_eng", "ml_supervised", "ml_unsupervised"],
    "NLP Engineer": ["prog_python", "dl_transformer", "nlp_core", "ml_evaluation"],
    "Computer Vision Engineer": ["prog_python", "dl_cnn", "cv_detection", "cv_pose"],
    "AI Researcher": ["math_linear_algebra", "math_calculus", "math_probability", "dl_transformer", "gen_diffusion", "rl_basics"],
    "MLOps Engineer": ["prog_python", "ml_evaluation", "mlops_deploy", "ds_eda"],
};


export class OmniAICareerRoadmapEngine {
    private skillTree: SkillNode[];
    private userProgress: Map<string, Set<string>> = new Map();

    constructor() {
        this.skillTree = [...SKILL_TREE];
    }

    /**
     * Generates a personalized learning path for a target role.
     */
    public generateLearningPath(
        userId: string,
        targetRole: string,
        completedSkillIds: string[] = []
    ): { success: boolean; value?: LearningPath; error?: Error } {
        const requirements = ROLE_REQUIREMENTS[targetRole];
        if (!requirements) {
            const roles = Object.keys(ROLE_REQUIREMENTS).join(", ");
            return { success: false, error: new Error(`Unknown role. Available: ${roles}`) };
        }

        const completed = new Set(completedSkillIds);
        this.userProgress.set(userId, completed);

        // Resolve all required skills including prerequisites (topological order)
        const allRequired = this.resolvePrerequisites(requirements);
        const remaining = allRequired.filter((s) => !completed.has(s.id));
        const totalHours = remaining.reduce((sum, s) => sum + s.estimatedHours, 0);
        const progress = allRequired.length > 0
            ? Math.round(((allRequired.length - remaining.length) / allRequired.length) * 100)
            : 0;

        return {
            success: true,
            value: {
                userId, targetRole,
                requiredSkills: remaining,
                completedSkills: completedSkillIds,
                totalHours,
                progressPercent: progress,
            },
        };
    }

    /**
     * Resolves all prerequisites recursively in topological order.
     */
    private resolvePrerequisites(skillIds: string[]): SkillNode[] {
        const visited = new Set<string>();
        const result: SkillNode[] = [];

        const visit = (id: string) => {
            if (visited.has(id)) return;
            visited.add(id);
            const node = this.skillTree.find((s) => s.id === id);
            if (node) {
                for (const prereq of node.prerequisites) {
                    visit(prereq);
                }
                result.push(node);
            }
        };

        for (const id of skillIds) {
            visit(id);
        }
        return result;
    }

    /**
     * Returns available AI career roles.
     */
    public listRoles(): { success: boolean; value: Record<string, number> } {
        const roles: Record<string, number> = {};
        for (const [role, skills] of Object.entries(ROLE_REQUIREMENTS)) {
            const resolved = this.resolvePrerequisites(skills);
            roles[role] = resolved.reduce((s, n) => s + n.estimatedHours, 0);
        }
        return { success: true, value: roles };
    }

    /**
     * Maps a skill to its relevant OMNI engine.
     */
    public getEngineMapping(skillId: string): { success: boolean; value?: string; error?: Error } {
        const node = this.skillTree.find((s) => s.id === skillId);
        if (!node) return { success: false, error: new Error("Skill not found.") };
        return { success: true, value: node.omniEngine || "No engine mapping." };
    }

    public evaluateHealth(): Record<string, any> {
        return {
            engine: "OmniAICareerRoadmapEngine",
            layer: "Interface",
            status: "healthy",
            totalSkills: this.skillTree.length,
            totalRoles: Object.keys(ROLE_REQUIREMENTS).length,
            learned_from: "AMAI-GmbH/AI-Expert-Roadmap",
        };
    }

    // --- Registry Interface ---
    diagnostics(): Record<string, unknown> {
        return {
            engine: "OmniAICareerRoadmapEngine",
            version: "1.0.0",
            status: "operational",
            layer: "ui",
            language: "TypeScript",
        };
    }
}
