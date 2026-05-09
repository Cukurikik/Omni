export interface ReviewComment {
    line: number;
    severity: 'low' | 'medium' | 'high';
    message: string;
}

export class CodeReviewCommentUI {
    private container: HTMLElement;

    constructor(containerId: string) {
        const el = document.getElementById(containerId);
        if (!el) throw new Error(`Container ${containerId} not found`);
        this.container = el;
    }

    public renderComments(comments: ReviewComment[]): void {
        if (comments.length === 0) {
            this.container.innerHTML = `<div style="padding: 10px; background: #e6ffe6; color: #006600; border-radius: 4px; font-family: Inter, sans-serif;">LGTM! No issues found.</div>`;
            return;
        }

        let html = `<div style="font-family: Inter, sans-serif; display: flex; flex-direction: column; gap: 10px;">`;
        
        for (const c of comments) {
            let bgColor = c.severity === 'high' ? '#ffe6e6' : (c.severity === 'medium' ? '#fffae6' : '#f0f0f5');
            let textColor = c.severity === 'high' ? '#cc0000' : (c.severity === 'medium' ? '#b38600' : '#333');
            
            html += `
                <div style="background: ${bgColor}; color: ${textColor}; padding: 12px; border-left: 4px solid ${textColor}; border-radius: 4px;">
                    <div style="font-weight: bold; margin-bottom: 4px;">Line ${c.line} (${c.severity.toUpperCase()})</div>
                    <div>${c.message}</div>
                </div>
            `;
        }
        
        html += `</div>`;
        this.container.innerHTML = html;
    }
}
