export class OmniResult<T, E> { constructor(public isOk: boolean, public value?: T, public error?: E) {} }
export class DustAgentPanel {
    private maxAgents = 100;
    private agents = 0;
    addAgent(name: string): OmniResult<boolean, string> {
        if (name.length > 256) return new OmniResult(false, undefined, "Name too long");
        if (this.agents >= this.maxAgents) return new OmniResult(false, undefined, "Agent display limit");
        this.agents++; return new OmniResult(true, true);
    }
}
