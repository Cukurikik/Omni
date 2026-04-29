class OmniResult{constructor(i,v,e){this.isOk=i;this.value=v;this.error=e;}}
class KVPressStreamManager{
    constructor(){this.MAX_STREAMS=500;this.streams=new Map();}
    createStream(id,modelId,ratio){
        if(this.streams.size>=this.MAX_STREAMS)return new OmniResult(false,null,new Error("Stream limit"));
        if(ratio<=0||ratio>1)return new OmniResult(false,null,new Error("Invalid ratio"));
        this.streams.set(id,{modelId,ratio,tokens:0});
        return new OmniResult(true,id,null);
    }
    pushTokens(id,count){
        const s=this.streams.get(id);
        if(!s)return new OmniResult(false,null,new Error("Stream not found"));
        s.tokens+=count;
        if(s.tokens>131072)return new OmniResult(false,null,new Error("Token limit 128K"));
        return new OmniResult(true,s.tokens,null);
    }
}
module.exports={KVPressStreamManager,OmniResult};
