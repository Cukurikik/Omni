// OMNI Interface Layer: autolabel_reviewer.ts
// React hook / Logic block for AutoLabel manual review queue.
// Bound: Fixed 50 items per review page to keep DOM fast.

export const MAX_REVIEW_PAGE_SIZE = 50;

export class OmniError extends Error {
    code: number;
    constructor(code: number, message: string) {
        super(message);
        this.code = code;
    }
}

export class OmniResult<T> {
    data: T | null;
    error: OmniError | null;
    constructor(data: T | null, error: OmniError | null = null) {
        this.data = data;
        this.error = error;
    }
}

export interface LabelItem {
    id: string;
    text: string;
    suggestedLabel: string;
    confidence: number;
}

export class AutoLabelReviewer {
    private currentQueue: LabelItem[] = [];

    public loadPage(items: LabelItem[]): OmniResult<boolean> {
        if (items.length > MAX_REVIEW_PAGE_SIZE) {
            return new OmniResult<boolean>(
                null, 
                new OmniError(1, `Review page size strictly bounded to ${MAX_REVIEW_PAGE_SIZE}.`)
            );
        }
        
        this.currentQueue = [...items];
        return new OmniResult<boolean>(true);
    }

    public getQueue(): LabelItem[] {
        return this.currentQueue;
    }

    public approveItem(id: string): void {
        this.currentQueue = this.currentQueue.filter(item => item.id !== id);
    }
}
