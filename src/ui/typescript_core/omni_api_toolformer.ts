export interface ToolCall {
    toolName: string;
    argument: string;
}

export class OmniToolformerAPI {
    /** OMNI Interface Layer: Toolformer API */
    public static formatInjectString(call: ToolCall): string {
        return `[API: ${call.toolName}(${call.argument})]`;
    }
}
