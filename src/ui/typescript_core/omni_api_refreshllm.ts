export interface KnowledgeEdit {
    subject: string;
    target: string;
    value: string;
}

export class OmniRefreshLLMAPI {
    /** OMNI Interface Layer: RefreshLLM API */
    public static compileEditRequest(edit: KnowledgeEdit): string {
        return `EDIT_GRAPH: (s: ${edit.subject}) -[:has]-> (t: ${edit.target}) = ${edit.value}`;
    }

    public static isValidEdit(edit: KnowledgeEdit): boolean {
        return edit.subject.length > 0 && edit.value.length > 0;
    }
}
