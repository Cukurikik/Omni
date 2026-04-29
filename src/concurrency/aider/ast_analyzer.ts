// OMNI AIDER: AST Analyzer
// TypeScript logic using concurrent worker threads to parse and analyze ASTs of massive codebases.
// Helps Aider build the "repository map".
// Source: paul-gauthier/aider

import { Worker, isMainThread, parentPort, workerData } from 'worker_threads';
import * as path from 'path';
import * as fs from 'fs';

// This would use tree-sitter in a real implementation
export type ASTNode = {
    type: string;
    name?: string;
    start_row: number;
    end_row: number;
};

export type FileAnalysisResult = {
    filepath: string;
    classes: string[];
    functions: string[];
    error?: string;
};

if (isMainThread) {
    // MAIN THREAD LOGIC
    export class OmniASTAnalyzer {
        private workerScript: string;

        constructor() {
            this.workerScript = __filename;
        }

        public async analyzeFiles(filepaths: string[]): Promise<FileAnalysisResult[]> {
            const promises = filepaths.map(filepath => this.runWorker(filepath));
            return Promise.all(promises);
        }

        private runWorker(filepath: string): Promise<FileAnalysisResult> {
            return new Promise((resolve, reject) => {
                const worker = new Worker(this.workerScript, { workerData: { filepath } });

                worker.on('message', (result: FileAnalysisResult) => resolve(result));
                worker.on('error', (err) => resolve({ filepath, classes: [], functions: [], error: err.message }));
                worker.on('exit', (code) => {
                    if (code !== 0) resolve({ filepath, classes: [], functions: [], error: `Worker stopped with exit code ${code}` });
                });
            });
        }
    }
} else {
    // WORKER THREAD LOGIC
    const { filepath } = workerData;

    try {
        const content = fs.readFileSync(filepath, 'utf-8');
        const lines = content.split('\n');
        
        const classes: string[] = [];
        const functions: string[] = [];

        // Mock Tree-sitter regex parsing
        lines.forEach(line => {
            const classMatch = line.match(/class\s+([A-Za-z0-9_]+)/);
            if (classMatch) classes.push(classMatch[1]);

            const fnMatch = line.match(/def\s+([A-Za-z0-9_]+)/) || line.match(/function\s+([A-Za-z0-9_]+)/);
            if (fnMatch) functions.push(fnMatch[1]);
        });

        const result: FileAnalysisResult = {
            filepath,
            classes,
            functions
        };

        parentPort?.postMessage(result);
    } catch (e: any) {
        parentPort?.postMessage({ filepath, classes: [], functions: [], error: e.message } as FileAnalysisResult);
    }
}
