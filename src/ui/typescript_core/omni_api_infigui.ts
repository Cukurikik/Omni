export interface GUIAction {
    elementId: string;
    actionType: 'CLICK' | 'TYPE' | 'SCROLL';
    value?: string;
}

export class OmniInfiGUIAPI {
    /** OMNI Interface Layer: InfiGUI API */
    public static createAction(elementId: string, type: 'CLICK' | 'TYPE' | 'SCROLL', value?: string): GUIAction {
        if (!elementId) throw new Error("Element ID is required");
        return {
            elementId,
            actionType: type,
            value
        };
    }

    public static serializeSequence(actions: GUIAction[]): string {
        return actions.map(a => `${a.actionType}@${a.elementId}`).join(' -> ');
    }
}
