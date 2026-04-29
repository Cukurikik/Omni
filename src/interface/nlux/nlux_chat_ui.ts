export class OmniResult<T, E> { constructor(public isOk: boolean, public value?: T, public error?: E) {} }
export class NLUXChatUI {
    private maxMessages = 10000;
    private maxMsgLen = 32768;
    private messageCount = 0;
    sendMessage(text: string): OmniResult<boolean, string> {
        if (text.length > this.maxMsgLen) return new OmniResult(false, undefined, "Message exceeds 32KB");
        if (this.messageCount >= this.maxMessages) return new OmniResult(false, undefined, "Chat history limit");
        this.messageCount++;
        return new OmniResult(true, true);
    }
}
