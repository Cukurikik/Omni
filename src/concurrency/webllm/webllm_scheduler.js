class OmniResult{constructor(i,v,e){this.isOk=i;this.value=v;this.error=e;}}
class WebLLMScheduler{
    constructor(){this.MAX_SESSIONS=100;this.sessions=new Map();}
    createSession(id,modelId){
        if(this.sessions.size>=this.MAX_SESSIONS)return new OmniResult(false,null,new Error("Session limit"));
        if(!modelId||modelId.length>256)return new OmniResult(false,null,new Error("Invalid model ID"));
        this.sessions.set(id,{modelId,tokens:0,active:true,startTime:Date.now()});
        return new OmniResult(true,id,null);
    }
    processToken(id,token){
        const s=this.sessions.get(id);
        if(!s||!s.active)return new OmniResult(false,null,new Error("No session"));
        if(s.tokens>131072)return new OmniResult(false,null,new Error("Context limit 128K"));
        s.tokens++;return new OmniResult(true,s.tokens,null);
    }
    endSession(id){this.sessions.delete(id);return new OmniResult(true,true,null);}
}
module.exports={WebLLMScheduler,OmniResult};
