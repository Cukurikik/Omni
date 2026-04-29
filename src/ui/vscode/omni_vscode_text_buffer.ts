// OMNI VSCode Text Buffer Engine — Interface Layer (TypeScript)
// Absorbing microsoft/vscode file editor bounds
// Deterministic Piece Table layout manipulation limits sequence mapping

export type EditorResult<T> = {
    ok: boolean;
    value: T | null;
    error: string;
};

export interface EditorPiece {
    bufferIndex: number; // 0 = original, 1 = append
    startOffset: number;
    length: number;
}

export class OmniVscodeTextBuffer {
    private edits_run: number = 0;
    
    private originalBuffer: string = "";
    private addBuffer: string = "";
    private pieceTable: EditorPiece[] = [];

    constructor(initialString: string) {
        this.originalBuffer = initialString;
        if (initialString.length > 0) {
            this.pieceTable.push({
                bufferIndex: 0,
                startOffset: 0,
                length: initialString.length
            });
        }
    }

    /**
     * Executes VSCode piece table insertion mapping bound complexity without complete copy geometry.
     */
    public insert_text(offset: number, text: string): EditorResult<boolean> {
        try {
            if (offset < 0) return { ok: false, value: false, error: "Invalid geometric offset limit." };
            if (!text) return { ok: true, value: true, error: "" }; // noop

            this.edits_run++;
            let currentLength = 0;
            let targetPieceIndex = -1;
            let splitOffset = 0;

            for (let i = 0; i < this.pieceTable.length; i++) {
                const piece = this.pieceTable[i];
                if (offset >= currentLength && offset < currentLength + piece.length) {
                    targetPieceIndex = i;
                    splitOffset = offset - currentLength;
                    break;
                }
                currentLength += piece.length;
            }

            const addOffset = this.addBuffer.length;
            this.addBuffer += text;
            const newPiece: EditorPiece = { bufferIndex: 1, startOffset: addOffset, length: text.length };

            if (targetPieceIndex === -1 && offset === currentLength) {
                 // Append to end of buffer bounds
                 this.pieceTable.push(newPiece);
            } else if (targetPieceIndex !== -1) {
                const originalPiece = this.pieceTable[targetPieceIndex];
                
                const leftPiece: EditorPiece = {
                    bufferIndex: originalPiece.bufferIndex,
                    startOffset: originalPiece.startOffset,
                    length: splitOffset
                };
                
                const rightPiece: EditorPiece = {
                    bufferIndex: originalPiece.bufferIndex,
                    startOffset: originalPiece.startOffset + splitOffset,
                    length: originalPiece.length - splitOffset
                };

                // Splice structural map
                const replacements = [];
                if (leftPiece.length > 0) replacements.push(leftPiece);
                replacements.push(newPiece);
                if (rightPiece.length > 0) replacements.push(rightPiece);

                this.pieceTable.splice(targetPieceIndex, 1, ...replacements);
            } else {
                 return { ok: false, value: false, error: "VscodeError: Offset exceeds topological mapping limits." };
            }

            return { ok: true, value: true, error: "" };
        } catch (e: any) {
            return { ok: false, value: false, error: `Buffer Panic: ${e.message}` };
        }
    }

    public get_content(): EditorResult<string> {
        try {
            let output = "";
            for (const piece of this.pieceTable) {
                const buf = piece.bufferIndex === 0 ? this.originalBuffer : this.addBuffer;
                output += buf.substr(piece.startOffset, piece.length);
            }
            return { ok: true, value: output, error: "" };
        } catch (e: any) {
            return { ok: false, value: null, error: `Read Panic: ${e.message}` };
        }
    }

    public diagnostics(): Record<string, any> {
        return {
            engine: "OmniVscodeTextBuffer",
            edits_mapped: this.edits_run,
            pieces: this.pieceTable.length,
            status: "Operational"
        };
    }
}
