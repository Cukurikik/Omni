// @omni-domain Business Layer (Langcorn Temporal)
export type OmniResult<T,E=Error> = {ok:true;data:T}|{ok:false;error:E};
export class TemporalError extends Error {}

export class LangcornTemporalWorkflow {
  private steps: Array<{name:string;fn:()=>Promise<any>;timeout:number}> = [];
  addStep(name:string, fn:()=>Promise<any>, timeout=30000) {
    this.steps.push({name,fn,timeout});
  }
  async execute(): Promise<OmniResult<any[]>> {
    try {
      const results: any[] = [];
      for (const step of this.steps) {
        const result = await Promise.race([step.fn(), new Promise((_,rej)=>setTimeout(()=>rej(new Error(`Timeout: ${step.name}`)),step.timeout))]);
        results.push({step: step.name, result});
      }
      return {ok:true,data:results};
    } catch(e) { return {ok:false,error:new TemporalError(`Workflow failed: ${e}`)}; }
  }
}
