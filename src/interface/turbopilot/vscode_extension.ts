// OMNI TURBOPILOT: VSCode Extension Logic
// TypeScript implementation of a VSCode InlineCompletionItemProvider connecting to a local turbopilot instance.
// Source: ravenscroftj/turbopilot

import * as vscode from 'vscode';
import axios from 'axios';

export class TurbopilotCompletionProvider implements vscode.InlineCompletionItemProvider {
    private apiUrl: string;
    private debounceTimer: NodeJS.Timeout | null = null;
    private requestDelayMs = 300; // Debounce to prevent flooding local CPU

    constructor() {
        // Points to the local turbopilot server running GGML
        this.apiUrl = vscode.workspace.getConfiguration('turbopilot').get('endpoint', 'http://127.0.0.1:8000/completions');
    }

    public async provideInlineCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        context: vscode.InlineCompletionContext,
        token: vscode.CancellationToken
    ): Promise<vscode.InlineCompletionItem[] | vscode.InlineCompletionList | null> {
        
        // Context Gathering
        const prefix = document.getText(new vscode.Range(new vscode.Position(0, 0), position));
        
        // Debounce requests
        if (this.debounceTimer) {
            clearTimeout(this.debounceTimer);
        }

        return new Promise((resolve) => {
            this.debounceTimer = setTimeout(async () => {
                if (token.isCancellationRequested) {
                    resolve(null);
                    return;
                }

                try {
                    const response = await axios.post(this.apiUrl, {
                        prompt: prefix,
                        max_tokens: 64,
                        temperature: 0.2,
                        stop: ["\n\n"]
                    }, {
                        headers: { 'Content-Type': 'application/json' },
                        timeout: 5000 // 5 second timeout for edge inference
                    });

                    if (token.isCancellationRequested || !response.data.choices) {
                        resolve(null);
                        return;
                    }

                    const completionText = response.data.choices[0].text;
                    resolve([new vscode.InlineCompletionItem(completionText)]);

                } catch (error) {
                    console.error("Turbopilot completion failed:", error);
                    resolve(null);
                }
            }, this.requestDelayMs);
        });
    }
}
