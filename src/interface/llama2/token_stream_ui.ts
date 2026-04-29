export interface OmniResult<T> {
    value: T | null;
    error: string | null;
    isOk: boolean;
}

export class TokenStreamUI {
    public renderToken(token: string): OmniResult<boolean> {
        if (!token) {
            return { value: false, error: "Empty token", isOk: false };
        }

        // TypeScript UI logic for smooth rendering of incoming LLM tokens
        process.stdout.write(token);
        
        return { value: true, error: null, isOk: true };
    }
}
