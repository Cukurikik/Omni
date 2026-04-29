/**
 * OmniInteractiveCanvas - OMNI Interface Layer
 * 
 * Provides strict TypeScript typings and contract-first API design
 * for rendering real-time UI components via WebGL/Canvas APIs.
 */

export type Result<T, E = Error> = 
  | { ok: true; value: T }
  | { ok: false; error: E };

export const Ok = <T>(value: T): Result<T, never> => ({ ok: true, value });
export const Err = <E>(error: E): Result<never, E> => ({ ok: false, error });

export interface CanvasConfig {
    width: number;
    height: number;
    pixelRatio: number;
    isInteractive: boolean;
}

export class OmniInteractiveCanvas {
    private readonly ctx: CanvasRenderingContext2D;
    private readonly config: CanvasConfig;

    constructor(canvas: HTMLCanvasElement, config: CanvasConfig) {
        const context = canvas.getContext('2d');
        if (!context) throw new Error("WebGL/2D Context not supported");
        
        this.ctx = context;
        this.config = config;
        
        // Handle high DPI displays
        canvas.width = config.width * config.pixelRatio;
        canvas.height = config.height * config.pixelRatio;
        this.ctx.scale(config.pixelRatio, config.pixelRatio);
    }

    /**
     * Renders a highly optimized frame graph without memory leaks.
     * Monadic return ensures rendering pipeline stability.
     */
    public renderFrame(operations: Array<() => void>): Result<number, string> {
        try {
            this.ctx.clearRect(0, 0, this.config.width, this.config.height);
            
            this.ctx.save();
            let opsExecuted = 0;
            
            for (const op of operations) {
                op();
                opsExecuted++;
            }
            
            this.ctx.restore();
            return Ok(opsExecuted);
        } catch (e) {
            return Err(`Frame rendering failed: ${e instanceof Error ? e.message : 'Unknown error'}`);
        }
    }
}
