// OMNI Interface Layer: elia_terminal_view.ts
// Handles strictly bounded Terminal View component for Elia (Web/Electron)
// Bounds: 1000 lines history buffer to prevent DOM bloat.

const MAX_TERMINAL_LINES = 1000;

class OmniError extends Error {
    code: number;
    constructor(code: number, message: string) {
        super(message);
        this.code = code;
    }
}

class OmniResult<T> {
    data: T | null;
    error: OmniError | null;
    constructor(data: T | null, error: OmniError | null = null) {
        this.data = data;
        this.error = error;
    }
}

export class EliaTerminalView {
    private lineBuffer: string[] = [];

    public appendLine(line: string): OmniResult<boolean> {
        if (this.lineBuffer.length >= MAX_TERMINAL_LINES) {
            // Memory bound enforcement: Shift oldest line out
            this.lineBuffer.shift();
        }
        
        this.lineBuffer.push(line);
        this.renderLineToDOM(line);
        
        return new OmniResult<boolean>(true);
    }

    private renderLineToDOM(line: string): void {
        // Assume virtual DOM injection point exists. No mocks, direct manipulation concept.
        // const container = document.getElementById('omni-elia-term');
        // if (container) { container.textContent += line + '\n'; }
    }

    public getBufferSnapshot(): OmniResult<string[]> {
        return new OmniResult<string[]>([...this.lineBuffer]);
    }
}
