// @omni-domain Business Layer (MindNLP Infra)
export type OmniResult<T,E=Error> = {ok:true;data:T}|{ok:false;error:E};
export class InfraError extends Error {}

export class MindNLPInfra {
  private services: Map<string,{url:string;status:string;health:number}> = new Map();
  register(name:string, url:string) {
    if(!name||!url) return {ok:false,error:new InfraError("Name and URL required.")} as OmniResult<boolean>;
    this.services.set(name,{url,status:"healthy",health:100});
    return {ok:true,data:true} as OmniResult<boolean>;
  }
  healthCheck(): OmniResult<{name:string;status:string;health:number}[]> {
    const results = Array.from(this.services.entries()).map(([name,s])=>({name,...s}));
    return {ok:true,data:results};
  }
}
