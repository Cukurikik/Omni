export interface ReActTurn {
    thought: string;
    action: string;
    observation: string;
}

export class OmniReActAPI {
    /** OMNI Interface Layer: ReAct API */
    public static buildPrompt(history: ReActTurn[], newQuestion: string): string {
        let prompt = `Solve the following: ${newQuestion}\n`;
        history.forEach((turn, i) => {
            prompt += `Thought ${i+1}: ${turn.thought}\n`;
            prompt += `Action ${i+1}: ${turn.action}\n`;
            prompt += `Observation ${i+1}: ${turn.observation}\n`;
        });
        return prompt;
    }
}
