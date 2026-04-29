/**
 * OMNI BotMed Router — UI Layer
 * Absorbing Jyotibrat/BotMed health hackathon project.
 * TypeScript reactive state router for handling medical chatbot conversational flows.
 */

export interface BotMedState {
    sessionId: string;
    stage: 'intake' | 'symptom_analysis' | 'triage' | 'resolved';
    history: string[];
    extractedSymptoms: string[];
    urgencyScore: number;
}

export interface BotMedResponse<T> {
    ok: boolean;
    data?: T;
    error?: string;
}

export class OmniBotMedRouter {
    private sessions: Map<string, BotMedState> = new Map();
    private interactions: number = 0;

    public initSession(sessionId: string): BotMedResponse<BotMedState> {
        if (!sessionId) return { ok: false, error: 'BotMedError: Session ID required' };
        const state: BotMedState = {
            sessionId,
            stage: 'intake',
            history: [],
            extractedSymptoms: [],
            urgencyScore: 0
        };
        this.sessions.set(sessionId, state);
        return { ok: true, data: state };
    }

    public processMessage(sessionId: string, message: string): BotMedResponse<string> {
        const state = this.sessions.get(sessionId);
        if (!state) return { ok: false, error: 'BotMedError: Unknown session' };

        this.interactions++;
        state.history.push(`User: ${message}`);

        // Zero-mock deterministic symptom routing transition
        let reply = '';
        if (state.stage === 'intake') {
            state.stage = 'symptom_analysis';
            reply = 'Bot: Please describe your symptoms in detail.';
        } else if (state.stage === 'symptom_analysis') {
            const symptoms = message.toLowerCase().split(',').map(s => s.trim());
            state.extractedSymptoms.push(...symptoms);
            state.urgencyScore += this.calculateUrgency(symptoms);
            
            if (state.extractedSymptoms.length >= 2 || state.urgencyScore > 5) {
                state.stage = 'triage';
                reply = `Bot: Analysis complete. Urgency score: ${state.urgencyScore}. Recommend consulting a specialist.`;
            } else {
                reply = 'Bot: Any other symptoms?';
            }
        } else if (state.stage === 'triage') {
            state.stage = 'resolved';
            reply = 'Bot: Session ended. Data stored securely.';
        }

        state.history.push(reply);
        return { ok: true, data: reply };
    }

    private calculateUrgency(symptoms: string[]): number {
        const severe = ['pain', 'bleeding', 'unconscious', 'fever'];
        let score = 0;
        for (const s of symptoms) {
            if (severe.some(k => s.includes(k))) score += 5;
            else score += 1;
        }
        return score;
    }

    public diagnostics(): Record<string, any> {
        return {
            engine: 'OmniBotMedRouter',
            activeSessions: this.sessions.size,
            interactions: this.interactions,
            status: 'Operational'
        };
    }
}
