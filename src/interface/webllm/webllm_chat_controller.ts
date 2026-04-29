interface OmniResult<T>{isOk:boolean;value:T|null;error:string|null;}
interface SessionConfig{modelId:string;contextLen:number;}
class WebLLMChatController{
    private sessions:Map<string,SessionConfig>=new Map();
    private readonly MAX_SESSIONS=100;
    createSession(id:string,config:SessionConfig):OmniResult<string>{
        if(this.sessions.size>=this.MAX_SESSIONS)return{isOk:false,value:null,error:"Session limit"};
        if(!config.modelId)return{isOk:false,value:null,error:"Missing model ID"};
        if(config.contextLen>131072)return{isOk:false,value:null,error:"Context exceeds 128K"};
        this.sessions.set(id,config);return{isOk:true,value:id,error:null};
    }
    destroySession(id:string):OmniResult<boolean>{
        if(!this.sessions.has(id))return{isOk:false,value:null,error:"Session not found"};
        this.sessions.delete(id);return{isOk:true,value:true,error:null};
    }
}
export{WebLLMChatController};
