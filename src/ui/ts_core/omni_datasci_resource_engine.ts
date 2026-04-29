// ===========================================================================
// OMNI DATASCI RESOURCE ENGINE (SEMESTER 5 — BATCH 13)
// ===========================================================================
// Absorbed From  : academic/awesome-datascience
// Logic Inherited: Interface Layer (Data Science Resource Catalog & Discovery)
// ===========================================================================
//
// KNOWLEDGE ABSORBED:
//   awesome-datascience is a curated repository of data science resources:
//   tutorials, books, courses, tools, datasets, blogs, competitions, etc.
//   OMNI absorbs its taxonomy to build a structured resource discovery
//   engine that routes learners to the right materials.
//

export type ResourceCategory =
    | "course" | "book" | "tutorial" | "tool" | "dataset"
    | "blog" | "competition" | "podcast" | "newsletter" | "community";

export type DifficultyLevel = "beginner" | "intermediate" | "advanced";

export type DSTopicArea =
    | "statistics" | "machine_learning" | "deep_learning" | "data_engineering"
    | "visualization" | "nlp" | "computer_vision" | "big_data" | "mlops" | "general";

export interface DSResource {
    id: string;
    title: string;
    category: ResourceCategory;
    topic: DSTopicArea;
    difficulty: DifficultyLevel;
    url: string;
    description: string;
    tags: string[];
    rating: number;         // 1-5
}

// Curated resource catalog derived from awesome-datascience
const RESOURCE_CATALOG: DSResource[] = [
    // Courses
    { id: "r001", title: "Andrew Ng's Machine Learning (Coursera)", category: "course", topic: "machine_learning", difficulty: "beginner", url: "https://coursera.org/learn/machine-learning", description: "Foundational ML course covering regression, classification, neural networks", tags: ["ml", "supervised", "coursera"], rating: 5 },
    { id: "r002", title: "Fast.ai Practical Deep Learning", category: "course", topic: "deep_learning", difficulty: "intermediate", url: "https://course.fast.ai", description: "Top-down deep learning course with hands-on PyTorch projects", tags: ["dl", "pytorch", "practical"], rating: 5 },
    { id: "r003", title: "Stanford CS229 Machine Learning", category: "course", topic: "machine_learning", difficulty: "advanced", url: "https://cs229.stanford.edu", description: "Rigorous mathematical foundations of ML algorithms", tags: ["ml", "theory", "stanford"], rating: 5 },

    // Books
    { id: "r004", title: "Hands-On ML with Scikit-Learn & TensorFlow", category: "book", topic: "machine_learning", difficulty: "intermediate", url: "https://oreilly.com", description: "Practical ML book by Aurélien Géron", tags: ["sklearn", "tensorflow", "practical"], rating: 5 },
    { id: "r005", title: "Deep Learning (Goodfellow et al.)", category: "book", topic: "deep_learning", difficulty: "advanced", url: "https://deeplearningbook.org", description: "The definitive deep learning textbook", tags: ["dl", "theory", "math"], rating: 5 },
    { id: "r006", title: "Python for Data Analysis (Wes McKinney)", category: "book", topic: "data_engineering", difficulty: "beginner", url: "https://wesmckinney.com/book", description: "Essential Pandas and NumPy guide by the creator of Pandas", tags: ["pandas", "numpy", "python"], rating: 4 },

    // Tools
    { id: "r007", title: "Jupyter Notebook", category: "tool", topic: "general", difficulty: "beginner", url: "https://jupyter.org", description: "Interactive notebook environment for data science", tags: ["notebook", "python", "interactive"], rating: 5 },
    { id: "r008", title: "Apache Spark", category: "tool", topic: "big_data", difficulty: "advanced", url: "https://spark.apache.org", description: "Distributed computing framework for large-scale data processing", tags: ["spark", "distributed", "big-data"], rating: 4 },
    { id: "r009", title: "MLflow", category: "tool", topic: "mlops", difficulty: "intermediate", url: "https://mlflow.org", description: "Open-source platform for ML lifecycle management", tags: ["mlops", "tracking", "deployment"], rating: 4 },

    // Datasets
    { id: "r010", title: "Kaggle Datasets", category: "dataset", topic: "general", difficulty: "beginner", url: "https://kaggle.com/datasets", description: "Thousands of free datasets for practice and competitions", tags: ["kaggle", "free", "diverse"], rating: 5 },
    { id: "r011", title: "UCI Machine Learning Repository", category: "dataset", topic: "machine_learning", difficulty: "beginner", url: "https://archive.ics.uci.edu/ml", description: "Classic ML benchmark datasets", tags: ["uci", "benchmark", "classic"], rating: 4 },

    // Competitions
    { id: "r012", title: "Kaggle Competitions", category: "competition", topic: "general", difficulty: "intermediate", url: "https://kaggle.com/competitions", description: "Data science competitions with prizes and leaderboards", tags: ["kaggle", "competition", "prize"], rating: 5 },

    // Visualization
    { id: "r013", title: "D3.js", category: "tool", topic: "visualization", difficulty: "advanced", url: "https://d3js.org", description: "JavaScript library for data-driven visualizations", tags: ["d3", "javascript", "interactive"], rating: 5 },
    { id: "r014", title: "Matplotlib & Seaborn Guide", category: "tutorial", topic: "visualization", difficulty: "beginner", url: "https://matplotlib.org", description: "Python plotting libraries for statistical visualization", tags: ["matplotlib", "seaborn", "python"], rating: 4 },

    // NLP
    { id: "r015", title: "Hugging Face Hub", category: "tool", topic: "nlp", difficulty: "intermediate", url: "https://huggingface.co", description: "Model hub for pre-trained NLP and ML models", tags: ["transformers", "models", "nlp"], rating: 5 },
];


export class OmniDatasciResourceEngine {
    private catalog: DSResource[];

    constructor() {
        this.catalog = [...RESOURCE_CATALOG];
    }

    /**
     * Searches resources by keyword across title, description, and tags.
     */
    public search(query: string): { success: boolean; value: DSResource[] } {
        const q = query.toLowerCase();
        const results = this.catalog.filter(
            (r) =>
                r.title.toLowerCase().includes(q) ||
                r.description.toLowerCase().includes(q) ||
                r.tags.some((t) => t.includes(q))
        );
        return { success: true, value: results };
    }

    /**
     * Filters resources by category and/or difficulty.
     */
    public filter(options: {
        category?: ResourceCategory;
        topic?: DSTopicArea;
        difficulty?: DifficultyLevel;
    }): { success: boolean; value: DSResource[] } {
        let results = [...this.catalog];
        if (options.category) results = results.filter((r) => r.category === options.category);
        if (options.topic) results = results.filter((r) => r.topic === options.topic);
        if (options.difficulty) results = results.filter((r) => r.difficulty === options.difficulty);
        return { success: true, value: results };
    }

    /**
     * Returns the top-rated resources.
     */
    public topRated(limit: number = 5): { success: boolean; value: DSResource[] } {
        const sorted = [...this.catalog].sort((a, b) => b.rating - a.rating);
        return { success: true, value: sorted.slice(0, limit) };
    }

    /**
     * Returns catalog statistics.
     */
    public getStats(): Record<string, any> {
        const byCat: Record<string, number> = {};
        const byTopic: Record<string, number> = {};
        for (const r of this.catalog) {
            byCat[r.category] = (byCat[r.category] || 0) + 1;
            byTopic[r.topic] = (byTopic[r.topic] || 0) + 1;
        }
        return { totalResources: this.catalog.length, byCategory: byCat, byTopic: byTopic };
    }

    public evaluateHealth(): Record<string, any> {
        return {
            engine: "OmniDatasciResourceEngine", layer: "Interface", status: "healthy",
            catalogSize: this.catalog.length,
            categories: new Set(this.catalog.map((r) => r.category)).size,
            learned_from: "academic/awesome-datascience",
        };
    }

    // --- Registry Interface ---
    diagnostics(): Record<string, unknown> {
        return {
            engine: "OmniDatasciResourceEngine",
            version: "1.0.0",
            status: "operational",
            layer: "ui",
            language: "TypeScript",
        };
    }
}
