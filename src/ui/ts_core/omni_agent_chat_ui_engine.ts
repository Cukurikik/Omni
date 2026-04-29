// OMNI MOTHER — SEMESTER 14 BATCH 36
// TypeScript — Interface Layer (OMNI Zero-Mock Implementation)
// Implements production-grade AI Agent UI State Machine for chat interfaces.
// Absorbs patterns from: github.com/open-webui/open-webui, Dify

export type AgentUIState =
    | "idle"
    | "awaiting_input"
    | "thinking"
    | "streaming"
    | "tool_calling"
    | "error"
    | "completed";

export interface ChatMessage {
    id: string;
    role: "user" | "assistant" | "system" | "tool";
    content: string;
    timestamp: number;
    tokenCount: number;
    toolName?: string;
    metadata?: Record<string, unknown>;
}

export interface ConversationState {
    conversationId: string;
    messages: ChatMessage[];
    currentState: AgentUIState;
    totalTokens: number;
    maxTokens: number;
    isStreaming: boolean;
    streamBuffer: string;
}

export type UIResult<T> =
    | { value: T; isOk: true; error: null }
    | { value: null; isOk: false; error: string };

/**
 * AI Agent Chat UI State Machine Engine.
 *
 * Manages the complete lifecycle of an AI chat conversation:
 * idle → awaiting_input → thinking → streaming → completed
 *                                  ↘ tool_calling → thinking
 *                                  ↘ error
 *
 * Implements exact state transitions from Open WebUI patterns.
 */
export class OmniAgentChatUIEngine {
    private conversations: Map<string, ConversationState> = new Map();

    /**
     * Creates a new conversation session.
     *
     * @param conversationId - Unique conversation identifier
     * @param maxTokens - Maximum token budget for this conversation
     * @returns UIResult with the initial conversation state
     */
    createConversation(
        conversationId: string,
        maxTokens: number = 128000
    ): UIResult<ConversationState> {
        if (!conversationId) {
            return { value: null, isOk: false, error: "Conversation ID must be non-empty." };
        }
        if (this.conversations.has(conversationId)) {
            return { value: null, isOk: false, error: `Conversation '${conversationId}' already exists.` };
        }
        if (maxTokens <= 0) {
            return { value: null, isOk: false, error: "maxTokens must be > 0." };
        }

        const state: ConversationState = {
            conversationId,
            messages: [],
            currentState: "idle",
            totalTokens: 0,
            maxTokens,
            isStreaming: false,
            streamBuffer: "",
        };

        this.conversations.set(conversationId, state);
        return { value: state, isOk: true, error: null };
    }

    /**
     * Adds a user message and transitions to "thinking" state.
     *
     * @param conversationId - Target conversation
     * @param content - User message content
     * @returns UIResult of updated state
     */
    sendUserMessage(
        conversationId: string,
        content: string
    ): UIResult<ConversationState> {
        const conv = this.conversations.get(conversationId);
        if (!conv) {
            return { value: null, isOk: false, error: `Conversation '${conversationId}' not found.` };
        }
        if (conv.currentState !== "idle" && conv.currentState !== "completed" && conv.currentState !== "awaiting_input") {
            return { value: null, isOk: false, error: `Cannot send message in state '${conv.currentState}'.` };
        }
        if (!content.trim()) {
            return { value: null, isOk: false, error: "Message content must be non-empty." };
        }

        const tokenEstimate = Math.ceil(content.length / 4); // ~4 chars per token
        if (conv.totalTokens + tokenEstimate > conv.maxTokens) {
            return { value: null, isOk: false, error: "Token budget exceeded." };
        }

        const message: ChatMessage = {
            id: `msg_${conv.messages.length + 1}`,
            role: "user",
            content,
            timestamp: Date.now(),
            tokenCount: tokenEstimate,
        };

        conv.messages.push(message);
        conv.totalTokens += tokenEstimate;
        conv.currentState = "thinking";

        return { value: { ...conv }, isOk: true, error: null };
    }

    /**
     * Starts streaming response — transitions from "thinking" to "streaming".
     */
    startStreaming(conversationId: string): UIResult<ConversationState> {
        const conv = this.conversations.get(conversationId);
        if (!conv) {
            return { value: null, isOk: false, error: `Conversation not found.` };
        }
        if (conv.currentState !== "thinking") {
            return { value: null, isOk: false, error: `Cannot stream from state '${conv.currentState}'.` };
        }

        conv.currentState = "streaming";
        conv.isStreaming = true;
        conv.streamBuffer = "";

        return { value: { ...conv }, isOk: true, error: null };
    }

    /**
     * Appends a token chunk to the stream buffer.
     * Called for each SSE chunk from the LLM API.
     */
    appendStreamChunk(conversationId: string, chunk: string): UIResult<string> {
        const conv = this.conversations.get(conversationId);
        if (!conv) {
            return { value: null, isOk: false, error: "Conversation not found." };
        }
        if (conv.currentState !== "streaming") {
            return { value: null, isOk: false, error: "Not in streaming state." };
        }

        conv.streamBuffer += chunk;
        return { value: conv.streamBuffer, isOk: true, error: null };
    }

    /**
     * Completes streaming — finalizes assistant message, transitions to "completed".
     */
    completeStreaming(conversationId: string): UIResult<ConversationState> {
        const conv = this.conversations.get(conversationId);
        if (!conv) {
            return { value: null, isOk: false, error: "Conversation not found." };
        }
        if (conv.currentState !== "streaming") {
            return { value: null, isOk: false, error: "Not in streaming state." };
        }

        const tokenEstimate = Math.ceil(conv.streamBuffer.length / 4);
        const message: ChatMessage = {
            id: `msg_${conv.messages.length + 1}`,
            role: "assistant",
            content: conv.streamBuffer,
            timestamp: Date.now(),
            tokenCount: tokenEstimate,
        };

        conv.messages.push(message);
        conv.totalTokens += tokenEstimate;
        conv.isStreaming = false;
        conv.streamBuffer = "";
        conv.currentState = "completed";

        return { value: { ...conv }, isOk: true, error: null };
    }

    /**
     * Transitions to "tool_calling" state when the LLM requests a tool call.
     */
    startToolCall(conversationId: string, toolName: string): UIResult<ConversationState> {
        const conv = this.conversations.get(conversationId);
        if (!conv) {
            return { value: null, isOk: false, error: "Conversation not found." };
        }
        if (conv.currentState !== "thinking" && conv.currentState !== "streaming") {
            return { value: null, isOk: false, error: `Cannot start tool call from state '${conv.currentState}'.` };
        }

        conv.currentState = "tool_calling";

        const message: ChatMessage = {
            id: `msg_${conv.messages.length + 1}`,
            role: "tool",
            content: `Calling tool: ${toolName}`,
            timestamp: Date.now(),
            tokenCount: 0,
            toolName,
        };

        conv.messages.push(message);
        return { value: { ...conv }, isOk: true, error: null };
    }

    /**
     * Reports error state.
     */
    reportError(conversationId: string, errorMessage: string): UIResult<ConversationState> {
        const conv = this.conversations.get(conversationId);
        if (!conv) {
            return { value: null, isOk: false, error: "Conversation not found." };
        }

        conv.currentState = "error";
        conv.isStreaming = false;

        return { value: { ...conv }, isOk: true, error: null };
    }

    /**
     * Returns engine diagnostics.
     */
    diagnostics(): Record<string, unknown> {
        return {
            engine: "OmniAgentChatUIEngine",
            layer: "ui/typescript",
            activeConversations: this.conversations.size,
            status: "operational",
            learnedFrom: "open-webui/open-webui, Dify",
        };
    }
}
