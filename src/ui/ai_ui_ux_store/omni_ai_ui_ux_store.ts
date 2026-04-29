/**
 * OMNI AI UI UX Component Store — UI Layer
 * Absorbing AaronCWacker/AI-UI-UX-JS
 * Centralized State Tree for managing an ecosystem of intelligent living UI components.
 */

export interface UiComponentState {
    id: string;
    type: 'threejs' | 'mediapipe' | 'canvas' | 'markdown';
    isVisible: boolean;
    dataPayload: any;
    lastUpdated: number;
}

export interface AiUiUxResult<T> {
    ok: boolean;
    data?: T;
    error?: string;
}

export class OmniAiUiUxStore {
    private components: Map<string, UiComponentState> = new Map();
    private updateCounter: number = 0;

    public registerComponent(id: string, type: UiComponentState['type']): AiUiUxResult<boolean> {
        if (!id) return { ok: false, error: 'UiUxError: Component ID required' };
        if (this.components.has(id)) return { ok: false, error: 'UiUxError: Component already registered' };
        
        this.components.set(id, {
            id, type, isVisible: true, dataPayload: null, lastUpdated: Date.now()
        });
        return { ok: true, data: true };
    }

    public dispatchUpdate(id: string, payload: any): AiUiUxResult<number> {
        const comp = this.components.get(id);
        if (!comp) return { ok: false, error: 'UiUxError: Unknown component' };

        comp.dataPayload = payload;
        comp.lastUpdated = Date.now();
        this.updateCounter++;

        return { ok: true, data: comp.lastUpdated };
    }

    public toggleVisibility(id: string): AiUiUxResult<boolean> {
        const comp = this.components.get(id);
        if (!comp) return { ok: false, error: 'UiUxError: Unknown component' };

        comp.isVisible = !comp.isVisible;
        this.updateCounter++;
        return { ok: true, data: comp.isVisible };
    }

    public getSnapshot(): Record<string, UiComponentState> {
        const snapshot: Record<string, UiComponentState> = {};
        this.components.forEach((val, key) => { snapshot[key] = { ...val }; });
        return snapshot;
    }

    public diagnostics(): Record<string, any> {
        return {
            engine: 'OmniAiUiUxStore',
            componentsRegistered: this.components.size,
            updatesDispatched: this.updateCounter,
            status: 'Operational'
        };
    }
}
